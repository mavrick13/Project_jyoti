from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class InventoryCategory(str, enum.Enum):
    MOTOR = "motor"
    CONTROLLER = "controller"
    SOLAR_PANEL = "solar_panel"
    BOS = "bos"
    STRUCTURE = "structure"
    WIRE = "wire"
    PIPE = "pipe"


class InventoryStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(InventoryCategory), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 3hp, 5hp, 7.5hp, 520wp, 540wp
    specification = Column(String(50), nullable=True)  # 30, 50, 70, 100 (pump head)
    quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, default=10)  # Alert when stock goes below this
    unit_price = Column(Float, nullable=True)  # Optional price per unit
    supplier = Column(String(255), nullable=True)
    part_number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    document_url = Column(Text, nullable=True)  # Invoice, specification sheet, etc.
    status = Column(Enum(InventoryStatus), default=InventoryStatus.ACTIVE)
    location = Column(String(100), nullable=True)  # Warehouse location
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'in', 'out', 'adjustment'
    quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)  # 'farmer_dispatch', 'purchase', 'manual'
    reference_id = Column(String(50), nullable=True)  # farmer beneficiary_id, purchase order, etc.
    notes = Column(Text, nullable=True)
    unit_cost = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Relationships
    inventory = relationship("Inventory", foreign_keys=[inventory_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class FarmerDispatch(Base):
    __tablename__ = "farmer_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    farmer_beneficiary_id = Column(String(50), ForeignKey("farmers.beneficiary_id"), nullable=False)
    dispatch_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, dispatched, delivered, installed
    total_value = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Relationships
    farmer = relationship("Farmer", foreign_keys=[farmer_beneficiary_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class FarmerDispatchItem(Base):
    __tablename__ = "farmer_dispatch_items"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("farmer_dispatches.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)

    # Relationships
    dispatch = relationship("FarmerDispatch", foreign_keys=[dispatch_id])
    inventory = relationship("Inventory", foreign_keys=[inventory_id])