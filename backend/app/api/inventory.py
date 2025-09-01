from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, desc
from typing import Optional, List
import pandas as pd
import tempfile
import os
import math
from pathlib import Path

from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import settings
from ..models.user import User
from ..models.inventory import (
    Inventory, 
    InventoryTransaction, 
    FarmerDispatch, 
    FarmerDispatchItem,
    InventoryCategory,
    InventoryStatus
)
from ..schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryListResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
    FarmerDispatchCreate,
    FarmerDispatchResponse,
    InventoryStats,
    MotorSpecs,
    SolarPanelSpecs
)

router = APIRouter()

# Static template files directory
TEMPLATES_DIR = Path("static/templates")
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=InventoryListResponse)
async def get_inventory(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    specification: Optional[str] = Query(None, description="Filter by specification"),
    status: Optional[str] = Query(None, description="Filter by status"),
    low_stock_only: Optional[bool] = Query(False, description="Show only low stock items"),
    search: Optional[str] = Query(None, description="Search in description, part_number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated inventory list with filtering
    """
    query = db.query(Inventory)
    
    # Apply filters
    if category:
        query = query.filter(Inventory.category == category)
    if type:
        query = query.filter(Inventory.type == type)
    if specification:
        query = query.filter(Inventory.specification == specification)
    if status:
        query = query.filter(Inventory.status == status)
    if low_stock_only:
        query = query.filter(Inventory.quantity <= Inventory.min_stock_level)
    
    # Apply search
    if search:
        search_filter = or_(
            Inventory.description.ilike(f"%{search}%"),
            Inventory.part_number.ilike(f"%{search}%"),
            Inventory.supplier.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    # Add low stock flag
    inventory_responses = []
    for item in items:
        item_dict = InventoryResponse.from_orm(item).dict()
        item_dict['is_low_stock'] = item.quantity <= item.min_stock_level
        inventory_responses.append(InventoryResponse(**item_dict))
    
    # Calculate pagination info
    total_pages = math.ceil(total / page_size)
    
    return InventoryListResponse(
        items=inventory_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific inventory item
    """
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    response = InventoryResponse.from_orm(item)
    response.is_low_stock = item.quantity <= item.min_stock_level
    return response


@router.post("/", response_model=InventoryResponse)
async def create_inventory_item(
    item_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new inventory item
    """
    # Check if similar item already exists
    existing_item = db.query(Inventory).filter(
        Inventory.category == item_data.category,
        Inventory.type == item_data.type,
        Inventory.specification == item_data.specification
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Similar inventory item already exists. Consider updating the existing one."
        )
    
    # Create new inventory item
    new_item = Inventory(**item_data.dict(), created_by_user_id=current_user.user_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Create transaction record
    if item_data.quantity > 0:
        transaction = InventoryTransaction(
            inventory_id=new_item.id,
            transaction_type="in",
            quantity=item_data.quantity,
            previous_quantity=0,
            new_quantity=item_data.quantity,
            reference_type="initial_stock",
            notes="Initial stock entry",
            created_by_user_id=current_user.user_id
        )
        db.add(transaction)
        db.commit()
    
    response = InventoryResponse.from_orm(new_item)
    response.is_low_stock = new_item.quantity <= new_item.min_stock_level
    return response


@router.post("/bulk", response_model=dict)
async def create_inventory_bulk(
    items_data: List[InventoryCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple inventory items in bulk
    """
    created_items = []
    skipped_items = []
    
    for item_data in items_data:
        try:
            # Check if similar item already exists
            existing_item = db.query(Inventory).filter(
                Inventory.category == item_data.category,
                Inventory.type == item_data.type,
                Inventory.specification == item_data.specification
            ).first()
            
            if existing_item:
                # Update existing item quantity
                previous_qty = existing_item.quantity
                existing_item.quantity += item_data.quantity
                existing_item.updated_at = func.now()
                
                # Create transaction record
                transaction = InventoryTransaction(
                    inventory_id=existing_item.id,
                    transaction_type="in",
                    quantity=item_data.quantity,
                    previous_quantity=previous_qty,
                    new_quantity=existing_item.quantity,
                    reference_type="bulk_upload",
                    notes="Bulk upload - added to existing stock",
                    created_by_user_id=current_user.user_id
                )
                db.add(transaction)
                created_items.append(f"Updated: {item_data.category} {item_data.type}")
            else:
                # Create new inventory item
                new_item = Inventory(**item_data.dict(), created_by_user_id=current_user.user_id)
                db.add(new_item)
                db.flush()  # Get ID without committing
                
                # Create transaction record for new item
                if item_data.quantity > 0:
                    transaction = InventoryTransaction(
                        inventory_id=new_item.id,
                        transaction_type="in",
                        quantity=item_data.quantity,
                        previous_quantity=0,
                        new_quantity=item_data.quantity,
                        reference_type="bulk_upload",
                        notes="Bulk upload - new item",
                        created_by_user_id=current_user.user_id
                    )
                    db.add(transaction)
                
                created_items.append(f"Created: {item_data.category} {item_data.type}")
                
        except Exception as e:
            skipped_items.append(f"Error with {item_data.category} {item_data.type}: {str(e)}")
            continue
    
    db.commit()
    
    return {
        "message": "Bulk upload completed",
        "created_count": len(created_items),
        "skipped_count": len(skipped_items),
        "created_items": created_items,
        "skipped_items": skipped_items
    }


@router.post("/upload", response_model=dict)
async def upload_inventory_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload CSV/Excel file with inventory data
    """
    # Validate file format
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV, XLSX, and XLS files are allowed"
        )
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Read file based on format
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_file_path)
        else:
            df = pd.read_excel(temp_file_path)
        
        # Validate required columns
        required_columns = ['category', 'type', 'quantity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process data
        items_data = []
        for _, row in df.iterrows():
            try:
                # Handle NaN values
                item_data = InventoryCreate(
                    category=str(row['category']).lower(),
                    type=str(row['type']) if pd.notna(row['type']) else "",
                    specification=str(row['specification']) if pd.notna(row.get('specification')) else None,
                    quantity=int(row['quantity']) if pd.notna(row['quantity']) else 0,
                    min_stock_level=int(row['min_stock_level']) if pd.notna(row.get('min_stock_level')) else 10,
                    unit_price=float(row['unit_price']) if pd.notna(row.get('unit_price')) else None,
                    supplier=str(row['supplier']) if pd.notna(row.get('supplier')) else None,
                    part_number=str(row['part_number']) if pd.notna(row.get('part_number')) else None,
                    description=str(row['description']) if pd.notna(row.get('description')) else None,
                    location=str(row['location']) if pd.notna(row.get('location')) else None
                )
                items_data.append(item_data)
            except Exception as e:
                continue  # Skip invalid rows
        
        # Use bulk create endpoint
        result = await create_inventory_bulk(items_data, db, current_user)
        
        return {
            **result,
            "file_name": file.filename,
            "total_rows_processed": len(df)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update inventory item
    """
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Track quantity changes
    previous_quantity = item.quantity
    
    # Update item with provided data
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # Create transaction record if quantity changed
    if 'quantity' in update_data and item.quantity != previous_quantity:
        transaction_type = "in" if item.quantity > previous_quantity else "out"
        quantity_change = abs(item.quantity - previous_quantity)
        
        transaction = InventoryTransaction(
            inventory_id=item.id,
            transaction_type=transaction_type,
            quantity=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=item.quantity,
            reference_type="manual_adjustment",
            notes="Manual quantity adjustment",
            created_by_user_id=current_user.user_id
        )
        db.add(transaction)
        db.commit()
    
    response = InventoryResponse.from_orm(item)
    response.is_low_stock = item.quantity <= item.min_stock_level
    return response


@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete inventory item (admin only)
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete inventory items"
        )
    
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Inventory item deleted successfully"}


@router.post("/dispatch", response_model=FarmerDispatchResponse)
async def dispatch_inventory_to_farmer(
    dispatch_data: FarmerDispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dispatch inventory items to a farmer (auto-decrements stock)
    """
    # Create dispatch record
    dispatch = FarmerDispatch(
        farmer_beneficiary_id=dispatch_data.farmer_beneficiary_id,
        notes=dispatch_data.notes,
        created_by_user_id=current_user.user_id
    )
    db.add(dispatch)
    db.flush()  # Get ID without committing
    
    total_value = 0
    dispatch_items = []
    
    for item_data in dispatch_data.items:
        inventory_id = item_data['inventory_id']
        quantity = item_data['quantity']
        unit_cost = item_data.get('unit_cost', 0)
        
        # Get inventory item
        inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item {inventory_id} not found"
            )
        
        # Check stock availability
        if inventory.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {inventory.category} {inventory.type}. Available: {inventory.quantity}, Requested: {quantity}"
            )
        
        # Update inventory quantity (auto-decrement)
        previous_qty = inventory.quantity
        inventory.quantity -= quantity
        
        # Update status if out of stock
        if inventory.quantity == 0:
            inventory.status = InventoryStatus.OUT_OF_STOCK
        
        # Create dispatch item record
        total_cost = quantity * unit_cost
        dispatch_item = FarmerDispatchItem(
            dispatch_id=dispatch.id,
            inventory_id=inventory_id,
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost
        )
        db.add(dispatch_item)
        dispatch_items.append(dispatch_item)
        
        # Create transaction record
        transaction = InventoryTransaction(
            inventory_id=inventory_id,
            transaction_type="out",
            quantity=quantity,
            previous_quantity=previous_qty,
            new_quantity=inventory.quantity,
            reference_type="farmer_dispatch",
            reference_id=dispatch_data.farmer_beneficiary_id,
            notes=f"Dispatched to farmer {dispatch_data.farmer_beneficiary_id}",
            unit_cost=unit_cost,
            created_by_user_id=current_user.user_id
        )
        db.add(transaction)
        
        total_value += total_cost
    
    # Update dispatch total value
    dispatch.total_value = total_value
    dispatch.status = "dispatched"
    
    db.commit()
    db.refresh(dispatch)
    
    return FarmerDispatchResponse.from_orm(dispatch)


@router.get("/stats/dashboard", response_model=InventoryStats)
async def get_inventory_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory dashboard statistics
    """
    # Total items and value
    total_items = db.query(func.sum(Inventory.quantity)).scalar() or 0
    
    # Calculate total value (quantity * unit_price for items that have price)
    total_value_query = db.query(
        func.sum(Inventory.quantity * Inventory.unit_price)
    ).filter(Inventory.unit_price.isnot(None)).scalar()
    total_value = total_value_query or 0
    
    # Low stock items
    low_stock_items = db.query(Inventory).filter(
        Inventory.quantity <= Inventory.min_stock_level
    ).count()
    
    # Out of stock items
    out_of_stock_items = db.query(Inventory).filter(
        Inventory.quantity == 0
    ).count()
    
    # Category breakdown
    category_stats = db.query(
        Inventory.category,
        func.count(Inventory.id).label('count'),
        func.sum(Inventory.quantity).label('total_quantity')
    ).group_by(Inventory.category).all()
    
    categories = {}
    for cat, count, qty in category_stats:
        categories[cat.value] = {
            "items": count,
            "total_quantity": qty or 0
        }
    
    # Recent transactions
    recent_transactions = db.query(InventoryTransaction).order_by(
        desc(InventoryTransaction.created_at)
    ).limit(10).all()
    
    return InventoryStats(
        total_items=total_items,
        total_value=total_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        categories=categories,
        recent_transactions=[InventoryTransactionResponse.from_orm(t) for t in recent_transactions]
    )


@router.get("/specs/motors", response_model=MotorSpecs)
async def get_motor_specifications():
    """
    Get motor specifications for UI dropdowns
    """
    return MotorSpecs()


@router.get("/specs/solar", response_model=SolarPanelSpecs)
async def get_solar_panel_specifications():
    """
    Get solar panel specifications for UI dropdowns
    """
    return SolarPanelSpecs()


# Template download endpoints
@router.get("/templates/excel")
async def download_excel_template():
    """
    Download Excel template for bulk inventory upload
    """
    template_path = TEMPLATES_DIR / "inventory_template.xlsx"
    
    # Create template if it doesn't exist
    if not template_path.exists():
        create_excel_template(template_path)
    
    return FileResponse(
        path=template_path,
        filename="inventory_bulk_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/templates/csv")
async def download_csv_template():
    """
    Download CSV template for bulk inventory upload
    """
    template_path = TEMPLATES_DIR / "inventory_template.csv"
    
    # Create template if it doesn't exist
    if not template_path.exists():
        create_csv_template(template_path)
    
    return FileResponse(
        path=template_path,
        filename="inventory_bulk_template.csv",
        media_type="text/csv"
    )


def create_excel_template(file_path: Path):
    """
    Create Excel template with sample data and instructions
    """
    sample_data = [
        {
            'category': 'motor',
            'type': '3hp',
            'specification': '30',
            'quantity': 10,
            'min_stock_level': 5,
            'unit_price': 15000.0,
            'supplier': 'Motor Supplier Ltd',
            'part_number': 'MOT-3HP-30',
            'description': '3HP motor with 30m head',
            'location': 'Warehouse A'
        },
        {
            'category': 'motor',
            'type': '5hp',
            'specification': '50',
            'quantity': 8,
            'min_stock_level': 3,
            'unit_price': 25000.0,
            'supplier': 'Motor Supplier Ltd',
            'part_number': 'MOT-5HP-50',
            'description': '5HP motor with 50m head',
            'location': 'Warehouse A'
        },
        {
            'category': 'controller',
            'type': '3hp',
            'specification': '',
            'quantity': 15,
            'min_stock_level': 5,
            'unit_price': 8000.0,
            'supplier': 'Control Systems Inc',
            'part_number': 'CTRL-3HP',
            'description': '3HP pump controller',
            'location': 'Warehouse B'
        },
        {
            'category': 'solar_panel',
            'type': '520wp',
            'specification': '',
            'quantity': 50,
            'min_stock_level': 20,
            'unit_price': 12000.0,
            'supplier': 'Solar Tech Ltd',
            'part_number': 'SOLAR-520',
            'description': '520W solar panel',
            'location': 'Warehouse C'
        }
    ]
    
    # Create Excel file with sample data
    df = pd.DataFrame(sample_data)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Inventory Data', index=False)
        
        # Create instructions sheet
        instructions = pd.DataFrame({
            'Column': ['category', 'type', 'specification', 'quantity', 'min_stock_level', 'unit_price', 'supplier', 'part_number', 'description', 'location'],
            'Required': ['Yes', 'Yes', 'No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No'],
            'Description': [
                'motor, controller, solar_panel, bos, structure, wire, pipe',
                '3hp, 5hp, 7.5hp, 520wp, 540wp',
                'For motors: 30, 50, 70, 100 (pump head)',
                'Stock quantity (number)',
                'Minimum stock level for alerts (default: 10)',
                'Unit price (optional)',
                'Supplier name (optional)',
                'Part number (optional)',
                'Item description (optional)',
                'Storage location (optional)'
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)


def create_csv_template(file_path: Path):
    """
    Create CSV template with sample data
    """
    sample_data = [
        ['motor', '3hp', '30', 10, 5, 15000.0, 'Motor Supplier Ltd', 'MOT-3HP-30', '3HP motor with 30m head', 'Warehouse A'],
        ['motor', '5hp', '50', 8, 3, 25000.0, 'Motor Supplier Ltd', 'MOT-5HP-50', '5HP motor with 50m head', 'Warehouse A'],
        ['controller', '3hp', '', 15, 5, 8000.0, 'Control Systems Inc', 'CTRL-3HP', '3HP pump controller', 'Warehouse B'],
        ['solar_panel', '520wp', '', 50, 20, 12000.0, 'Solar Tech Ltd', 'SOLAR-520', '520W solar panel', 'Warehouse C'],
        ['bos', '3hp', '', 12, 5, 5000.0, 'BOS Systems Ltd', 'BOS-3HP', '3HP Balance of System', 'Warehouse D'],
        ['structure', '5hp', '', 20, 8, 3000.0, 'Structure Co', 'STRUCT-5HP', '5HP mounting structure', 'Warehouse E'],
        ['wire', '7.5hp', '', 100, 20, 500.0, 'Cable Works', 'WIRE-7.5HP', '7.5HP system wiring', 'Warehouse F'],
        ['pipe', '3hp', '', 50, 15, 200.0, 'Pipe Industries', 'PIPE-3HP', '3HP system piping', 'Warehouse G']
    ]
    
    import csv
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['category', 'type', 'specification', 'quantity', 'min_stock_level', 
                        'unit_price', 'supplier', 'part_number', 'description', 'location'])
        # Write sample data
        writer.writerows(sample_data)