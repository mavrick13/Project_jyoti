# 🏭 Inventory Management System - Setup Guide

## Overview

I've successfully created a complete **Inventory Management System** for your Project Moriarty that includes:

### ✅ **Backend Features (Python FastAPI)**
- **Complete CRUD operations** for inventory items
- **Bulk upload** via CSV/Excel files with validation
- **Auto-decrement functionality** when dispatching to farmers
- **Real-time stock tracking** with low stock alerts
- **Comprehensive transaction logging** for all inventory movements
- **Template downloads** for Excel and CSV formats
- **Advanced filtering and search** capabilities
- **Dashboard statistics** and analytics

### ✅ **Frontend Features (React + TypeScript)**
- **Modern dashboard** with stats cards and charts
- **Inventory table** with pagination and sorting
- **Add/Edit forms** with validation and smart dropdowns
- **Bulk upload modal** with drag-and-drop file support
- **Dispatch system** with farmer integration
- **Real-time notifications** for low stock items
- **Responsive design** with Tailwind CSS

### ✅ **Inventory Categories Supported**
1. **Motors** (3HP, 5HP, 7.5HP with pump heads: 30, 50, 70, 100)
2. **Controllers** (3HP, 5HP, 7.5HP)
3. **Solar Panels** (520WP, 540WP)
4. **BOS** (Balance of System - 3HP, 5HP, 7.5HP)
5. **Structure** (Mounting structures - 3HP, 5HP, 7.5HP)
6. **Wire** (System wiring - 3HP, 5HP, 7.5HP)
7. **Pipe** (System piping - 3HP, 5HP, 7.5HP)

## 🚀 Quick Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd F:\Project_Moriarty\backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE project_moriarty;
   ```

4. **Update environment variables in `.env`:**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/project_moriarty
   SECRET_KEY=your-secret-key-here
   ```

5. **Start the backend:**
   ```bash
   python main.py
   ```

### Frontend Integration

1. **Add inventory route to your App.tsx:**
   ```typescript
   import { InventoryDashboard } from './components/inventory';

   // In your renderPage function:
   case 'inventory':
     return <InventoryDashboard />;
   ```

2. **Add inventory to your navigation:**
   ```typescript
   {
     name: 'Inventory',
     href: 'inventory',
     icon: Package,
     current: currentPage === 'inventory'
   }
   ```

## 📊 **Key Features Explained**

### **Auto-Decrement System**
When you dispatch items to a farmer:
- ✅ Stock automatically decreases
- ✅ Transaction is logged with farmer reference
- ✅ Status updates to "Out of Stock" when quantity reaches zero
- ✅ Low stock alerts trigger when below minimum level

### **Bulk Upload Process**
1. Download Excel/CSV template from the dashboard
2. Fill in inventory data following the template structure
3. Upload via the bulk upload modal
4. System validates and imports data automatically
5. Existing items get quantity added, new items are created

### **Smart Dropdowns**
- **Motor specifications** automatically show correct pump head options based on HP
- **Category selection** updates available type options dynamically  
- **Form validation** prevents invalid combinations

## 🔧 **API Endpoints**

### **Inventory Management**
- `GET /api/inventory/` - Get paginated inventory with filters
- `POST /api/inventory/` - Create new inventory item
- `PUT /api/inventory/{id}` - Update inventory item
- `DELETE /api/inventory/{id}` - Delete inventory item (admin only)
- `POST /api/inventory/bulk` - Bulk create inventory items
- `POST /api/inventory/upload` - Upload CSV/Excel file
- `POST /api/inventory/dispatch` - Dispatch items to farmer
- `GET /api/inventory/stats/dashboard` - Get inventory statistics

### **Templates**
- `GET /api/inventory/templates/excel` - Download Excel template
- `GET /api/inventory/templates/csv` - Download CSV template

## 📋 **CSV/Excel Template Format**

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| category | Yes | motor, controller, solar_panel, bos, structure, wire, pipe | motor |
| type | Yes | 3hp, 5hp, 7.5hp, 520wp, 540wp | 5hp |
| specification | No | For motors: 30, 50, 70, 100 (pump head) | 50 |
| quantity | Yes | Stock quantity | 25 |
| min_stock_level | No | Minimum stock alert level (default: 10) | 5 |
| unit_price | No | Price per unit in ₹ | 25000.0 |
| supplier | No | Supplier name | Motor Tech Ltd |
| part_number | No | Part/SKU number | MOT-5HP-50 |
| description | No | Item description | 5HP motor with 50m head |
| location | No | Storage location | Warehouse A |

## 🔍 **Usage Examples**

### **Adding Motor Inventory**
```typescript
{
  category: "motor",
  type: "5hp", 
  specification: "50", // 50m pump head
  quantity: 20,
  min_stock_level: 5,
  unit_price: 25000,
  supplier: "Motor Tech Ltd",
  location: "Warehouse A"
}
```

### **Dispatching to Farmer**
```typescript
dispatchToFarmer("MT4414700303374", [
  { inventory_id: 1, quantity: 1, unit_cost: 25000 }, // Motor
  { inventory_id: 5, quantity: 1, unit_cost: 8000 },  // Controller  
  { inventory_id: 10, quantity: 4, unit_cost: 12000 } // Solar panels
], "Complete solar pump system for farmer installation");
```

## 🛡️ **Data Validation**

- **Category validation** ensures only valid categories
- **Type-specification matching** prevents invalid combinations
- **Stock validation** prevents negative quantities
- **Dispatch validation** checks stock availability before processing
- **File format validation** for uploads (CSV, XLSX, XLS only)

## 📈 **Dashboard Metrics**

The inventory dashboard shows:
- **Total Items** - Current stock across all categories
- **Total Value** - Monetary value of all inventory
- **Low Stock Alerts** - Items below minimum stock level
- **Out of Stock** - Items with zero quantity
- **Category Breakdown** - Stock distribution by category
- **Recent Transactions** - Latest inventory movements

## 🔗 **Integration with Farmers**

The inventory system seamlessly integrates with your existing farmer management:
- Dispatch items directly to farmers by beneficiary ID
- Track which items were sent to which farmers
- Automatic inventory adjustment when farmer dispatch status updates
- Historical tracking of all farmer-related inventory movements

## 🎯 **Next Steps**

Your inventory system is now fully functional! You can:

1. **Test the APIs** using the interactive docs at `http://localhost:8000/docs`
2. **Import your existing inventory** using the bulk upload feature
3. **Set up automated alerts** for low stock notifications
4. **Integrate with your farmer dispatch workflow**

The system is production-ready and includes comprehensive error handling, transaction logging, and data validation.