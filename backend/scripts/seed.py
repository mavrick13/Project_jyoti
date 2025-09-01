import sys
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.farmer import Farmer
from app.core.database import Base

def seed_database():
    """
    Seed the database with initial data from Excel file
    """
    print("🌱 Starting database seeding...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users == 0:
            print("👤 Creating initial users...")
            
            # Create admin user
            admin_user = User(
                name="Admin User",
                email="admin@jyotielectrotech.com",
                phone="9999999999",
                role="Admin",
                password_hash=get_password_hash("admin123"),
                status="active"
            )
            db.add(admin_user)
            
            # Create some installer users
            installer1 = User(
                name="Installer One",
                email="installer1@jyotielectrotech.com",
                phone="8888888888",
                role="Employee",
                password_hash=get_password_hash("installer123"),
                status="active"
            )
            db.add(installer1)
            
            installer2 = User(
                name="Installer Two",
                email="installer2@jyotielectrotech.com",
                phone="7777777777",
                role="Employee",
                password_hash=get_password_hash("installer123"),
                status="active"
            )
            db.add(installer2)
            
            db.commit()
            print("✅ Users created successfully")
        else:
            print("👤 Users already exist, skipping user creation")
        
        # Check if farmers already exist
        existing_farmers = db.query(Farmer).count()
        if existing_farmers == 0:
            print("🚜 Seeding farmers from Excel file...")
            
            # Read Excel file if it exists
            excel_file = Path("database_with_dummy_data.xlsx")
            if excel_file.exists():
                # Read farmers sheet
                df = pd.read_excel(excel_file, sheet_name="Farmers")
                
                farmers_created = 0
                for _, row in df.iterrows():
                    try:
                        # Convert selection_date from Excel serial number to date
                        selection_date = None
                        if pd.notna(row.get('selection_date')):
                            if isinstance(row['selection_date'], (int, float)):
                                # Excel serial date
                                selection_date = pd.to_datetime('1900-01-01') + pd.Timedelta(days=int(row['selection_date'])-2)
                            else:
                                selection_date = pd.to_datetime(row['selection_date'])
                        
                        farmer = Farmer(
                            beneficiary_id=str(row['beneficiary_id']) if pd.notna(row.get('beneficiary_id')) else None,
                            beneficiary_name=str(row['beneficiary_name']) if pd.notna(row.get('beneficiary_name')) else "Unknown",
                            phone_no=str(int(row['phone_no'])) if pd.notna(row.get('phone_no')) else None,
                            aadhaar_no=str(row['aadhaar_no']) if pd.notna(row.get('aadhaar_no')) else None,
                            scheme=str(row['scheme']) if pd.notna(row.get('scheme')) else "MTS",
                            pumphp=str(row['pumphp']) if pd.notna(row.get('pumphp')) else None,
                            pumphead=str(row['pumphead']) if pd.notna(row.get('pumphead')) else None,
                            selection_date=selection_date.date() if selection_date else None,
                            circle_name=str(row['circle_name']) if pd.notna(row.get('circle_name')) else None,
                            taluka_name=str(row['taluka_name']) if pd.notna(row.get('taluka_name')) else None,
                            village_name=str(row['village_name']) if pd.notna(row.get('village_name')) else None,
                            installer_user_id=None,  # Will be assigned later
                            ld=str(row['ld']) if pd.notna(row.get('ld')) else None,
                            jsr_status=str(row['jsr_status']) if pd.notna(row.get('jsr_status')) else None,
                            dispatch_status=str(row['dispatch_status']) if pd.notna(row.get('dispatch_status')) else "Not Dispatched",
                            dispatch_date=None,
                            vehicle_no=str(row['vehicle_no']) if pd.notna(row.get('vehicle_no')) else None,
                            driver_info=str(row['driver_info']) if pd.notna(row.get('driver_info')) else None,
                            installation_status=str(row['installation_status']) if pd.notna(row.get('installation_status')) else "Not Started",
                            installation_remark=str(row['installation_remark']) if pd.notna(row.get('installation_remark')) else None,
                            icr_status=str(row['icr_status']) if pd.notna(row.get('icr_status')) else "Not Started",
                            photos=str(row['photos']) if pd.notna(row.get('photos')) else None,
                        )
                        
                        # Skip if beneficiary_id is None or empty
                        if farmer.beneficiary_id:
                            db.add(farmer)
                            farmers_created += 1
                            
                    except Exception as e:
                        print(f"⚠️  Error processing farmer row: {e}")
                        continue
                
                db.commit()
                print(f"✅ Created {farmers_created} farmers from Excel file")
                
            else:
                print("⚠️  Excel file not found, creating sample farmers...")
                # Create some sample farmers
                sample_farmers = [
                    Farmer(
                        beneficiary_id="SAMPLE001",
                        beneficiary_name="Sample Farmer One",
                        phone_no="9876543210",
                        scheme="MTS",
                        pumphp="5 HP",
                        pumphead="30",
                        circle_name="Test Circle",
                        taluka_name="Test Taluka",
                        village_name="Test Village",
                        dispatch_status="Done",
                        installation_status="Done",
                        icr_status="Done"
                    ),
                    Farmer(
                        beneficiary_id="SAMPLE002",
                        beneficiary_name="Sample Farmer Two",
                        phone_no="9876543211",
                        scheme="SADBHAV",
                        pumphp="7.5 HP",
                        pumphead="50",
                        circle_name="Test Circle",
                        taluka_name="Test Taluka",
                        village_name="Test Village 2",
                        dispatch_status="In Transit",
                        installation_status="Not Started",
                        icr_status="Not Started"
                    )
                ]
                
                for farmer in sample_farmers:
                    db.add(farmer)
                
                db.commit()
                print("✅ Sample farmers created successfully")
                
        else:
            print("🚜 Farmers already exist, skipping farmer creation")
    
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    
    finally:
        db.close()
    
    print("🎉 Database seeding completed!")


if __name__ == "__main__":
    seed_database()
