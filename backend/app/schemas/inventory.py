from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InventoryCategory(str, Enum):
    MOTOR = "motor"
    CONTROLLER = "controller"
    SOLAR_PANEL = "solar_panel"
    BOS = "bos"
    STRUCTURE = "structure"
    WIRE = "wire"
    PIPE = "pipe"


class InventoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class TransactionType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"


# Base Inventory schema
class InventoryBase(BaseModel):
    category: InventoryCategory
    type: str = Field(..., max_length=50)
    specification: Optional[str] = Field(None, max_length=50)
    quantity: int = Field(..., ge=0)
    min_stock_level: int = Field(10, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    supplier: Optional[str] = Field(None, max_length=255)
    part_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: InventoryStatus = InventoryStatus.ACTIVE


# Schema for creating inventory
class InventoryCreate(InventoryBase):
    pass


# Schema for updating inventory
class InventoryUpdate(BaseModel):
    category: Optional[InventoryCategory] = None
    type: Optional[str] = Field(None, max_length=50)
    specification: Optional[str] = Field(None, max_length=50)
    quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    supplier: Optional[str] = Field(None, max_length=255)
    part_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[InventoryStatus] = None


# Schema for inventory response
class InventoryResponse(InventoryBase):
    id: int
    document_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by_user_id: Optional[int] = None
    is_low_stock: bool = False

    class Config:
        from_attributes = True


# Schema for bulk inventory upload
class InventoryBulkCreate(BaseModel):
    items: List[InventoryCreate]


# Schema for inventory transactions
class InventoryTransactionCreate(BaseModel):
    inventory_id: int
    transaction_type: TransactionType
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None


class InventoryTransactionResponse(BaseModel):
    id: int
    inventory_id: int
    transaction_type: TransactionType
    quantity: int
    previous_quantity: int
    new_quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    created_at: datetime
    created_by_user_id: int

    class Config:
        from_attributes = True


# Schema for farmer dispatch
class FarmerDispatchCreate(BaseModel):
    farmer_beneficiary_id: str
    items: List[dict]  # [{"inventory_id": 1, "quantity": 2, "unit_cost": 100.0}]
    notes: Optional[str] = None


class FarmerDispatchItemResponse(BaseModel):
    id: int
    inventory_id: int
    quantity: int
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    inventory: InventoryResponse

    class Config:
        from_attributes = True


class FarmerDispatchResponse(BaseModel):
    id: int
    farmer_beneficiary_id: str
    dispatch_date: datetime
    status: str
    total_value: Optional[float] = None
    notes: Optional[str] = None
    items: List[FarmerDispatchItemResponse]

    class Config:
        from_attributes = True


# Schema for inventory list with pagination
class InventoryListResponse(BaseModel):
    items: List[InventoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Schema for inventory filters
class InventoryFilter(BaseModel):
    category: Optional[InventoryCategory] = None
    type: Optional[str] = None
    specification: Optional[str] = None
    status: Optional[InventoryStatus] = None
    low_stock_only: Optional[bool] = False
    search: Optional[str] = None


# Schema for inventory statistics
class InventoryStats(BaseModel):
    total_items: int
    total_value: float
    low_stock_items: int
    out_of_stock_items: int
    categories: dict
    recent_transactions: List[InventoryTransactionResponse]


# Schema for motor specifications (for UI dropdowns)
class MotorSpecs(BaseModel):
    hp_3: List[str] = ["30", "50", "70"]
    hp_5: List[str] = ["30", "50", "70", "100"]
    hp_7_5: List[str] = ["30", "50", "70", "100"]


class SolarPanelSpecs(BaseModel):
    types: List[str] = ["520wp", "540wp"]