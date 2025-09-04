# FastAPI Starter Template with Authentication

A production-ready, scalable FastAPI server template featuring comprehensive user management, JWT authentication, role-based access control, and Docker deployment. Built with modern Python tools and best practices.

## ✨ Key Features

### 🔐 **Authentication & Authorization**
- **JWT Authentication** with access and refresh tokens
- **Role-based Access Control** (Regular Users, Staff, Superusers)
- **Secure Password Hashing** with bcrypt
- **Token Refresh Mechanism** for seamless user experience
- **User Registration & Login** with validation

### 👥 **User Management System**
- **Complete User CRUD Operations** 
- **Admin Panel** for superuser management
- **Staff Dashboard** with read-only user access
- **User Profile Management** with password reset
- **Account Activation/Deactivation**
- **Role Promotion/Demotion** (Superuser ↔ Staff ↔ Regular User)

### 🗄️ **Database & Migration**
- **SQLModel** for type-safe database operations
- **PostgreSQL** with UUID primary keys
- **Alembic** for version-controlled database migrations
- **Database Session Management** with dependency injection

### 🐳 **Development & Deployment**
- **Docker & Docker Compose** for containerized development
- **Separate Environment Configurations** (`.env` for app, `.env.docker` for containers)
- **Health Checks** and monitoring endpoints
- **Hot Reload** development environment
- **Production-ready Dockerfile** with uv package manager

### 🛠️ **Developer Experience**
- **FastAPI** with automatic OpenAPI documentation
- **Pydantic V2** for robust data validation
- **Type Hints** throughout the codebase
- **CORS Support** for frontend integration
- **Comprehensive Error Handling**
- **Structured Logging**

## 📋 Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose**
- **uv** (recommended) or pip for dependency management

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd fastapi-server

# Copy environment templates
cp .env.example .env
cp .env.docker.example .env.docker
```

### 2. Configure Environment Variables

**Application Configuration (`.env`):**
```env
# Application Environment
ENVIRONMENT=local

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com

# Security Settings
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# Database Configuration (for local development)
POSTGRES_SERVER=localhost
POSTGRES_PORT=5442
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=fastapi_db

# Alembic Database URL
DATABASE_URL=postgresql+psycopg://fastapi_user:secure_password@localhost:5442/fastapi_db

# First Superuser Configuration
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=secure_admin_password
```

**Docker Database Configuration (`.env.docker`):**
```env
# Docker Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=docker_db_password
POSTGRES_DB=fastapi_app
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# The application will automatically:
# - Start PostgreSQL database
# - Run database migrations
# - Create the first superuser
# - Start the FastAPI server

# Access the application
open http://localhost:8000/docs
```

### 4. Manual Development Setup

```bash
# Start only the database
docker-compose up -d db

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Create superuser
uv run python scripts/create_superuser.py

# Start development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

### 🔗 **Endpoints Overview**

| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| **Authentication** |
| `POST` | `/api/v1/auth/register` | Register new user | Public |
| `POST` | `/api/v1/auth/login` | User login | Public |
| `POST` | `/api/v1/auth/token/refresh` | Refresh access token | Public |
| `POST` | `/api/v1/auth/token/test` | Test token validity | Authenticated |
| **User Profile** |
| `GET` | `/api/v1/user` | Get current user profile | Authenticated |
| `PUT` | `/api/v1/user` | Update current user profile | Authenticated |
| `PUT` | `/api/v1/user/reset-password` | Change password | Authenticated |
| `DELETE` | `/api/v1/user` | Delete current user | Authenticated |
| **Staff Dashboard** |
| `GET` | `/api/v1/staff/users` | List all users (read-only) | Staff/Admin |
| `GET` | `/api/v1/staff/users/{id}` | Get user details | Staff/Admin |
| `GET` | `/api/v1/staff/dashboard` | Staff dashboard stats | Staff/Admin |
| **Admin Management** |
| `GET` | `/api/v1/admin/users` | List all users with pagination | Admin |
| `POST` | `/api/v1/admin/users` | Create new user | Admin |
| `GET` | `/api/v1/admin/users/{id}` | Get user by ID | Admin |
| `PUT` | `/api/v1/admin/users/{id}` | Update user | Admin |
| `DELETE` | `/api/v1/admin/users/{id}` | Delete user | Admin |
| `PUT` | `/api/v1/admin/users/{id}/password` | Update user password | Admin |
| `PUT` | `/api/v1/admin/users/{id}/activate` | Activate user | Admin |
| `PUT` | `/api/v1/admin/users/{id}/deactivate` | Deactivate user | Admin |
| `PUT` | `/api/v1/admin/users/{id}/promote` | Promote to superuser | Admin |
| `PUT` | `/api/v1/admin/users/{id}/demote` | Demote from superuser | Admin |
| `PUT` | `/api/v1/admin/users/{id}/make-staff` | Grant staff privileges | Admin |
| `PUT` | `/api/v1/admin/users/{id}/remove-staff` | Remove staff privileges | Admin |
| `GET` | `/api/v1/admin/stats` | Comprehensive user statistics | Admin |
| **Health & Monitoring** |
| `GET` | `/` | Root endpoint | Public |
| `GET` | `/health` | Health check | Public |

### 🎯 **Interactive Documentation**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Complete Project Structure

```
fastapi-server/
├── 📁 app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   ├── utils.py                      # Utility functions (JWT token generation)
│   │
│   ├── 📁 api/                       # API layer
│   │   ├── __init__.py
│   │   ├── deps.py                   # Dependency injection (auth, database)
│   │   ├── v1_router.py             # API v1 router aggregator
│   │   └── 📁 v1/                   # API version 1 endpoints
│   │       ├── __init__.py
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── user.py              # User profile management
│   │       ├── staff.py             # Staff dashboard (read-only user management)
│   │       └── admin.py             # Admin user management (full CRUD)
│   │
│   ├── 📁 core/                      # Core application configuration
│   │   ├── __init__.py
│   │   ├── config.py                # Application settings (Pydantic Settings)
│   │   ├── security.py              # Security utilities (JWT, password hashing)
│   │   └── logger.py                # Logging configuration
│   │
│   ├── 📁 crud/                      # Database CRUD operations
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication CRUD
│   │   └── user.py                  # User CRUD operations
│   │
│   ├── 📁 db/                        # Database configuration
│   │   ├── __init__.py
│   │   └── session.py               # Database session management
│   │
│   ├── 📁 models/                    # SQLModel database models
│   │   ├── __init__.py
│   │   └── user.py                  # User and UserAuthProviderToken models
│   │
│   ├── 📁 schemas/                   # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── common.py                # Common schemas (Token, AuthResponse)
│   │   └── user.py                  # User-related schemas
│   │
│   └── 📁 services/                  # Business logic layer
│       └── __init__.py
│
├── 📁 alembic/                       # Database migrations
│   ├── env.py                       # Alembic environment configuration
│   ├── script.py.mako              # Migration template
│   ├── README                       # Alembic documentation
│   └── 📁 versions/                 # Migration files
│       ├── 3c242e501ef7_initial_migration.py
│       └── 58328a446c4a_add_is_staff_field_to_user_model.py
│
├── 📁 scripts/                       # Utility scripts
│   ├── create_superuser.py          # Create first superuser script
│   └── entrypoint.sh               # Docker entrypoint script
│
├── 📁 static/                        # Static files (if needed)
│
├── 📁 tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration
│   ├── test_user.py                 # User tests
│   └── api.http                     # HTTP client test files
│
├── 📄 Configuration Files
├── .env.example                     # Application environment template
├── .env.docker.example             # Docker database environment template
├── .gitignore                      # Git ignore rules
├── alembic.ini                     # Alembic configuration
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile                      # Docker build instructions
├── pyproject.toml                  # Project dependencies & settings
├── uv.lock                         # Dependency lock file
├── LICENSE                         # MIT License
├── README.md                       # This file
└── sample_endpoints.http           # Sample API requests
```

## 🔄 Database Management

### **Migration Commands**

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current migration
uv run alembic current

# Show migration history
uv run alembic history
```

### **Database Schema**

#### **User Model**
- `id` (UUID, Primary Key)
- `username` (Optional String)
- `email` (String, Unique, Indexed)
- `hashed_password` (Optional String)
- `is_active` (Boolean, default: True)
- `is_superuser` (Boolean, default: False)
- `is_staff` (Boolean, default: False)
- `last_login_at` (Optional DateTime)
- `first_name`, `last_name` (Optional Strings)
- `profile_picture` (Optional String URL)
- `bio` (Optional String)
- `created_at` (DateTime with timezone)

#### **UserAuthProviderToken Model**
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to User)
- `provider_name` (String) - e.g., 'google', 'facebook', 'form'
- `access_token` (String)
- `refresh_token` (Optional String)
- `expires_at` (Optional DateTime)

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_user.py

# Run tests in verbose mode
uv run pytest -v
```

## 🛡️ Security Features

### **Password Security**
- bcrypt hashing with salt
- Minimum password length validation
- Password change requires current password verification

### **JWT Security**
- HS256 algorithm
- Configurable token expiration
- Separate access and refresh tokens
- Token validation on protected endpoints

### **API Security**
- Role-based access control
- Input validation with Pydantic
- SQL injection prevention with SQLModel
- CORS configuration for cross-origin requests

## 🚀 Deployment

### **Environment Configurations**

**Development**
```env
ENVIRONMENT=local
SECRET_KEY=dev-secret-key
```

**Staging**
```env
ENVIRONMENT=staging
SECRET_KEY=staging-secret-key
```

**Production**
```env
ENVIRONMENT=production
SECRET_KEY=super-secure-production-key
# Docs are disabled in production for security
```

### **Docker Production Deployment**

```bash
# Build production image
docker build -t fastapi-server:latest .

# Run with production environment
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  --name fastapi-app \
  fastapi-server:latest
```

### **Docker Compose Production**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    restart: unless-stopped
  
  db:
    image: postgres:17.5
    env_file:
      - .env.docker.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔧 Configuration

### **Environment Variables Reference**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `local` | No |
| `SECRET_KEY` | JWT signing secret | Generated | Yes |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `3600` | No |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token lifetime | `10080` | No |
| `POSTGRES_SERVER` | Database host | - | Yes |
| `POSTGRES_PORT` | Database port | `5432` | No |
| `POSTGRES_USER` | Database user | - | Yes |
| `POSTGRES_PASSWORD` | Database password | - | Yes |
| `POSTGRES_DB` | Database name | - | Yes |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `[]` | No |
| `FIRST_SUPERUSER_EMAIL` | Initial admin email | - | Yes |
| `FIRST_SUPERUSER_PASSWORD` | Initial admin password | - | Yes |

## 📝 Usage Examples

### **Register a New User**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### **Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### **Access Protected Endpoint**

```bash
curl -X GET "http://localhost:8000/api/v1/user" \
  -H "Authorization: Bearer your-access-token"
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure tests pass**: `uv run pytest`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### **Development Guidelines**

- Follow Python PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 🐛 Troubleshooting

### **Common Issues**

**Database Connection Error**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**Migration Issues**
```bash
# Reset migrations (development only)
docker-compose down -v
docker-compose up -d db
uv run alembic upgrade head
```

**Permission Denied on entrypoint.sh**
```bash
# Make script executable
chmod +x scripts/entrypoint.sh
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - Library for interacting with SQL databases from Python code
- **Alembic** - Database migration tool for SQLAlchemy
- **Pydantic** - Data validation and settings management using Python type annotations
- **uv** - An extremely fast Python package installer and resolver