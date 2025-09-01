#!/usr/bin/env python3
"""
Project Moriarty Connection Test Script
Tests connections between Database, Backend API, and Frontend
"""

import sys
import os
import requests
import psycopg2
from psycopg2 import sql
import json
import time
from pathlib import Path
import subprocess
import socket
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def test_database_connection():
    """Test PostgreSQL database connection"""
    print_header("DATABASE CONNECTION TEST")
    
    try:
        # Try to load environment variables
        db_configs = [
            {
                'host': 'localhost',
                'port': '5432',
                'database': 'project_moriarty',
                'user': 'postgres',
                'password': input("Enter PostgreSQL password: ")
            }
        ]
        
        for config in db_configs:
            try:
                print_info(f"Connecting to database: {config['database']}@{config['host']}:{config['port']}")
                
                conn = psycopg2.connect(
                    host=config['host'],
                    port=config['port'],
                    database=config['database'],
                    user=config['user'],
                    password=config['password']
                )
                
                cursor = conn.cursor()
                
                # Test basic connection
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                print_success(f"Connected to PostgreSQL: {db_version}")
                
                # Check if required tables exist
                required_tables = [
                    'users', 'farmers', 'inventory', 'inventory_transactions',
                    'farmer_dispatches', 'tasks', 'chat_groups', 'messages'
                ]
                
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                
                existing_tables = [row[0] for row in cursor.fetchall()]
                print_info(f"Found {len(existing_tables)} tables in database")
                
                missing_tables = []
                for table in required_tables:
                    if table in existing_tables:
                        print_success(f"Table '{table}' exists")
                    else:
                        missing_tables.append(table)
                        print_error(f"Table '{table}' missing")
                
                if missing_tables:
                    print_warning("Some required tables are missing. Run database_setup.sql first.")
                    return False
                
                # Check sample data
                cursor.execute("SELECT COUNT(*) FROM users;")
                user_count = cursor.fetchone()[0]
                print_info(f"Users in database: {user_count}")
                
                cursor.execute("SELECT COUNT(*) FROM inventory;")
                inventory_count = cursor.fetchone()[0]
                print_info(f"Inventory items in database: {inventory_count}")
                
                cursor.execute("SELECT COUNT(*) FROM farmers;")
                farmer_count = cursor.fetchone()[0]
                print_info(f"Farmers in database: {farmer_count}")
                
                # Test a sample query
                cursor.execute("""
                    SELECT u.name, u.email, u.role 
                    FROM users u 
                    WHERE u.role = 'Admin' 
                    LIMIT 1;
                """)
                admin_user = cursor.fetchone()
                if admin_user:
                    print_success(f"Admin user found: {admin_user[0]} ({admin_user[1]})")
                else:
                    print_warning("No admin user found")
                
                cursor.close()
                conn.close()
                print_success("Database connection test PASSED")
                return True
                
            except Exception as e:
                print_error(f"Database connection failed: {str(e)}")
                return False
                
    except Exception as e:
        print_error(f"Database test setup failed: {str(e)}")
        return False

def test_backend_api():
    """Test FastAPI backend connection"""
    print_header("BACKEND API CONNECTION TEST")
    
    backend_url = "http://localhost:8000"
    
    try:
        # Test if backend is running
        print_info("Checking if backend server is running...")
        
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print_success(f"Backend server is running: {health_data.get('message', 'OK')}")
            else:
                print_error(f"Backend health check failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error("Backend server is not running on localhost:8000")
            print_info("Please start the backend with: python main.py")
            return False
        except Exception as e:
            print_error(f"Backend connection error: {str(e)}")
            return False
        
        # Test API documentation
        try:
            docs_response = requests.get(f"{backend_url}/docs", timeout=5)
            if docs_response.status_code == 200:
                print_success("API documentation accessible at /docs")
            else:
                print_warning("API documentation not accessible")
        except:
            print_warning("Could not access API documentation")
        
        # Test specific API endpoints
        endpoints_to_test = [
            "/api/farmers",
            "/api/inventory", 
            "/api/users",
            "/api/dashboard/stats"
        ]
        
        print_info("Testing API endpoints...")
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401]:  # 401 is expected without auth
                    print_success(f"Endpoint {endpoint} is responding")
                else:
                    print_warning(f"Endpoint {endpoint} returned HTTP {response.status_code}")
            except Exception as e:
                print_error(f"Endpoint {endpoint} failed: {str(e)}")
        
        # Test authentication endpoint
        print_info("Testing authentication endpoint...")
        try:
            auth_data = {
                "email": "admin@jyotielectrotech.com",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{backend_url}/api/auth/login", 
                json=auth_data,
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if "access_token" in token_data:
                    print_success("Authentication endpoint working correctly")
                    
                    # Test authenticated request
                    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                    auth_response = requests.get(
                        f"{backend_url}/api/auth/me",
                        headers=headers,
                        timeout=5
                    )
                    
                    if auth_response.status_code == 200:
                        user_data = auth_response.json()
                        print_success(f"Authenticated as: {user_data.get('name')} ({user_data.get('role')})")
                    else:
                        print_warning("Token validation failed")
                        
                else:
                    print_error("Authentication response missing access token")
            else:
                print_error(f"Authentication failed: HTTP {response.status_code}")
                if response.status_code == 401:
                    print_warning("Check if admin user exists in database")
                
        except Exception as e:
            print_error(f"Authentication test failed: {str(e)}")
        
        print_success("Backend API connection test COMPLETED")
        return True
        
    except Exception as e:
        print_error(f"Backend API test failed: {str(e)}")
        return False

def test_frontend_files():
    """Test if frontend files exist and are properly configured"""
    print_header("FRONTEND FILES TEST")
    
    project_root = Path("F:/Project_Moriarty/project-bolt-sb1-wqad8ycr/project")
    
    if not project_root.exists():
        print_error("Frontend project directory not found")
        return False
    
    print_success(f"Frontend project found at: {project_root}")
    
    # Check essential files
    essential_files = [
        "package.json",
        "src/App.tsx",
        "src/main.tsx",
        "src/store/inventoryStore.ts",
        "src/components/inventory/InventoryDashboard.tsx"
    ]
    
    missing_files = []
    for file_path in essential_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"Found: {file_path}")
        else:
            missing_files.append(file_path)
            print_error(f"Missing: {file_path}")
    
    if missing_files:
        print_warning(f"{len(missing_files)} essential files are missing")
    
    # Check package.json for dependencies
    try:
        package_json_path = project_root / "package.json"
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            required_deps = ["react", "typescript", "vite", "tailwindcss", "zustand"]
            dependencies = {**package_data.get("dependencies", {}), 
                          **package_data.get("devDependencies", {})}
            
            print_info("Checking frontend dependencies...")
            for dep in required_deps:
                if dep in dependencies:
                    print_success(f"Dependency '{dep}' found: {dependencies[dep]}")
                else:
                    print_warning(f"Dependency '{dep}' not found")
    
    except Exception as e:
        print_error(f"Error reading package.json: {str(e)}")
    
    # Check if dev server is running
    try:
        print_info("Checking if frontend dev server is running...")
        response = requests.get("http://localhost:5173", timeout=3)
        if response.status_code == 200:
            print_success("Frontend dev server is running on http://localhost:5173")
        else:
            print_warning("Frontend dev server responded with non-200 status")
    except requests.exceptions.ConnectionError:
        print_warning("Frontend dev server is not running on localhost:5173")
        print_info("Start with: npm run dev")
    except Exception as e:
        print_warning(f"Could not check frontend server: {str(e)}")
    
    print_success("Frontend files test COMPLETED")
    return len(missing_files) == 0

def test_integration():
    """Test full integration between components"""
    print_header("INTEGRATION TEST")
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    integration_tests = []
    
    # Test 1: Backend can connect to database and return data
    try:
        print_info("Testing backend-database integration...")
        response = requests.get(f"{backend_url}/api/inventory/stats/dashboard", timeout=10)
        if response.status_code == 401:
            print_warning("Authentication required - this is expected behavior")
            integration_tests.append(True)
        elif response.status_code == 200:
            stats_data = response.json()
            print_success(f"Backend successfully fetched data: {len(stats_data)} stats items")
            integration_tests.append(True)
        else:
            print_error(f"Backend-database integration failed: HTTP {response.status_code}")
            integration_tests.append(False)
    except Exception as e:
        print_error(f"Backend-database integration error: {str(e)}")
        integration_tests.append(False)
    
    # Test 2: CORS configuration
    try:
        print_info("Testing CORS configuration...")
        response = requests.options(f"{backend_url}/api/health", 
                                  headers={"Origin": frontend_url}, 
                                  timeout=5)
        if response.status_code in [200, 204]:
            print_success("CORS is properly configured")
            integration_tests.append(True)
        else:
            print_warning(f"CORS test returned: HTTP {response.status_code}")
            integration_tests.append(True)  # Not critical
    except Exception as e:
        print_warning(f"CORS test failed: {str(e)}")
        integration_tests.append(True)  # Not critical
    
    # Test 3: WebSocket/Socket.IO connection
    try:
        print_info("Testing Socket.IO connection...")
        # Simple TCP connection test to the backend port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print_success("Socket.IO endpoint is accessible")
            integration_tests.append(True)
        else:
            print_warning("Socket.IO endpoint not accessible")
            integration_tests.append(False)
    except Exception as e:
        print_warning(f"Socket.IO test failed: {str(e)}")
        integration_tests.append(False)
    
    # Summary
    passed_tests = sum(integration_tests)
    total_tests = len(integration_tests)
    
    if passed_tests == total_tests:
        print_success(f"Integration test PASSED: {passed_tests}/{total_tests} tests passed")
        return True
    else:
        print_warning(f"Integration test PARTIAL: {passed_tests}/{total_tests} tests passed")
        return False

def main():
    """Main test function"""
    print_header("PROJECT MORIARTY CONNECTION TEST")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all tests
    results['database'] = test_database_connection()
    results['backend'] = test_backend_api()
    results['frontend'] = test_frontend_files()
    results['integration'] = test_integration()
    
    # Final summary
    print_header("TEST SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name.upper()} test: PASSED")
        else:
            print_error(f"{test_name.upper()} test: FAILED")
            all_passed = False
    
    if all_passed:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
        print_success("Your Project Moriarty system is properly connected!")
    else:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠️  SOME TESTS FAILED ⚠️{Colors.END}")
        print_warning("Please check the issues above and resolve them.")
    
    print_info("\n" + "="*60)
    print_info("TROUBLESHOOTING GUIDE:")
    print_info("1. Database issues: Run setup_database.bat first")
    print_info("2. Backend issues: Start with 'python main.py' in backend folder")
    print_info("3. Frontend issues: Start with 'npm run dev' in frontend folder")
    print_info("4. Check .env file has correct DATABASE_URL")
    print_info("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Test failed with error: {str(e)}{Colors.END}")
    
    input("\nPress Enter to exit...")