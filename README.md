# Project_jyoti

 - Backend API

A FastAPI-based backend for the Project Moriarty farmer management system.

## Features

- 🔐 JWT Authentication
- 👥 User Management (Admin, Employee, Customer roles)
- 🚜 Farmer Management with comprehensive tracking
- 📊 Dashboard with statistics
- 🔍 Advanced filtering and search
- 📱 Real-time chat via Socket.IO
- 📝 Task Management (coming soon)
- 🔒 Role-based access control

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **Pydantic** - Data validation using Python type annotations
- **Socket.IO** - Real-time communication
- **JWT** - Secure authentication tokens
- **Uvicorn** - ASGI server

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── farmers.py    # Farmer management endpoints
│   │   ├── users.py      # User management endpoints
│   │   ├── tasks.py      # Task management endpoints
│   │   ├── chat.py       # Chat endpoints
│   │   └── dashboard.py  # Dashboard statistics
│   ├── core/             # Core functionality
│   │   ├── config.py     # Application settings
│   │   ├── database.py   # Database configuration
│   │   └── security.py   # Authentication & security
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py       # User model
│   │   ├── farmer.py     # Farmer model
│   │   ├── task.py       # Task model
│   │   └── message.py    # Message & chat models
│   └── schemas/          # Pydantic schemas
│       ├── user.py       # User schemas
│       └── farmer.py     # Farmer schemas
├── scripts/
│   └── seed.py           # Database seeding script
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip or conda

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd Project_Moriarty/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   ```sql
   CREATE DATABASE project_moriarty;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE project_moriarty TO postgres;
   ```

5. **Configure environment variables**:
   Update the `.env` file with your database credentials and other settings.

6. **Seed the database**:
   ```bash
   python scripts/seed.py
   ```

### Running the Application

1. **Start the development server**:
   ```bash
   uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh-token` - Refresh access token

### Farmers
- `GET /api/farmers/` - Get paginated farmers list with filters
- `GET /api/farmers/{beneficiary_id}` - Get specific farmer
- `POST /api/farmers/` - Create new farmer
- `PUT /api/farmers/{beneficiary_id}` - Update farmer
- `DELETE /api/farmers/{beneficiary_id}` - Delete farmer (admin only)
- `GET /api/farmers/stats/summary` - Get farmer statistics

### Users
- `GET /api/users/` - Get all users (admin only)
- `GET /api/users/{user_id}` - Get specific user
- `PUT /api/users/{user_id}` - Update user

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Real-time Features
- Socket.IO endpoint for real-time chat and notifications

## Database Schema

The database is designed to match your existing farmer management requirements:

### Users Table
- `user_id` (Primary Key)
- `name`, `email`, `phone`
- `role` (Admin, Employee, Customer)
- `password_hash`, `status`
- `created_at`, `updated_at`, `last_login`

### Farmers Table
- `beneficiary_id` (Primary Key)
- `beneficiary_name`, `phone_no`, `aadhaar_no`
- `scheme` (MTS, SADBHAV, SAYLIP, CROMPTON)
- `pumphp`, `pumphead`, `pumphp_combined` (computed)
- Location: `circle_name`, `taluka_name`, `village_name`
- Status tracking: `jsr_status`, `dispatch_status`, `installation_status`, `icr_status`
- Additional fields: `selection_date`, `dispatch_date`, `vehicle_no`, `driver_info`, etc.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Login** with email/password to get an access token
2. **Include the token** in the Authorization header: `Bearer <token>`
3. **Tokens expire** after 30 days (configurable)

### Default Users

After running the seed script, you'll have:

- **Admin**: `admin@jyotielectrotech.com` / `admin123`
- **Installer 1**: `installer1@jyotielectrotech.com` / `installer123`
- **Installer 2**: `installer2@jyotielectrotech.com` / `installer123`

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints wherever possible
- Write docstrings for functions and classes

### Adding New Endpoints
1. Create or update models in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Add API routes in `app/api/`
4. Update `main.py` to include new routes

### Database Migrations
For production deployments, consider using Alembic for database migrations:
```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Production Deployment

1. **Environment Variables**: Update `.env` with production values
2. **Database**: Use a production PostgreSQL instance
3. **ASGI Server**: Use Gunicorn with Uvicorn workers
4. **Security**: Enable HTTPS, update CORS settings
5. **Monitoring**: Add logging and health checks

Example production command:
```bash
gunicorn main:socket_app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Follow semantic commit messages

## License

[Your License Here]
