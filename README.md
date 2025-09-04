# FastAPI Server with SQLModel

A modern, scalable FastAPI server template with SQLModel, Alembic migrations, JWT authentication, and Docker support.

## 🚀 Features

- **FastAPI** with async/await support
- **SQLModel** for type-safe database operations
- **Alembic** for database migrations
- **JWT Authentication** with access and refresh tokens
- **Docker & Docker Compose** for easy deployment
- **Pydantic V2** for data validation
- **PostgreSQL** as the database
- **uv** for fast dependency management
- **CORS** support
- **Health checks** and proper logging
- **User management** with password hashing

## 📋 Prerequisites

- Python 3.12+
- Docker & Docker Compose
- uv (recommended) or pip

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd fastapi-server
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Environment Configuration
ENVIRONMENT=local

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5442
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_password
POSTGRES_DB=fastapi_db

# Alembic Database URL
DATABASE_URL=postgresql+psycopg://fastapi_user:fastapi_password@localhost:5442/fastapi_db

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=superuserpassword123
```

### 3. Install dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or if you prefer uv (optional):
```bash
uv sync
```

## 🐳 Running with Docker (Recommended)

### 1. Start the services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5442
- FastAPI application on port 8000

### 2. Create the first superuser

```bash
docker-compose exec app python scripts/create_superuser.py
```

### 3. Access the application

- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Local Development

### 1. Start PostgreSQL

```bash
docker-compose up -d db
```

### 2. Run migrations

```bash
alembic upgrade head
```

### 3. Create superuser

```bash
python scripts/create_superuser.py
```

### 4. Start the development server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/token/refresh` - Refresh access token
- `POST /api/v1/auth/token/test` - Test access token

### User Management

- `GET /api/v1/user` - Get current user profile
- `PUT /api/v1/user` - Update current user profile
- `PUT /api/v1/user/reset-password` - Change password
- `DELETE /api/v1/user` - Delete current user

### Health

- `GET /` - Root endpoint
- `GET /health` - Health check

## 🗄️ Database

### Creating migrations

```bash
alembic revision --autogenerate -m "Your migration message"
```

### Running migrations

```bash
alembic upgrade head
```

### Downgrading migrations

```bash
alembic downgrade -1
```

## 🧪 Testing

### Run tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Production Environment Variables

Make sure to set secure values for production:

```env
ENVIRONMENT=production
SECRET_KEY=your-very-secure-secret-key
POSTGRES_PASSWORD=very-secure-password
FIRST_SUPERUSER_PASSWORD=very-secure-superuser-password
```

### Docker Production Build

```bash
docker build -t fastapi-server .
docker run -p 8000:8000 --env-file .env fastapi-server
```

## 📁 Project Structure

```
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependencies
│   │   ├── v1_router.py         # API v1 router
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       └── user.py          # User endpoints
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   ├── logger.py            # Logging setup
│   │   └── security.py          # Security utilities
│   ├── crud/
│   │   ├── auth.py              # Authentication CRUD
│   │   └── user.py              # User CRUD
│   ├── db/
│   │   └── session.py           # Database session
│   ├── models/
│   │   └── user.py              # SQLModel models
│   ├── schemas/
│   │   ├── common.py            # Common schemas
│   │   └── user.py              # User schemas
│   ├── services/                # Business logic
│   ├── main.py                  # FastAPI app
│   └── utils.py                 # Utility functions
├── alembic/                     # Database migrations
├── scripts/
│   ├── start-backend.sh         # Startup script
│   └── create_superuser.py      # Create superuser script
├── tests/                       # Test files
├── docker-compose.yml           # Docker Compose config
├── Dockerfile                   # Docker config
├── pyproject.toml              # Project dependencies
└── .env.example                # Environment variables template
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.