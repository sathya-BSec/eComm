# E-Commerce Web Application

A modern full-stack e-commerce web application built with Next.js, Python FastAPI, and MySQL.

## 🚀 Features

- **Frontend**: Modern React/Next.js with TypeScript and Tailwind CSS
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: MySQL with full CRUD operations
- **Authentication**: 
  - JWT-based auth with secure password hashing
  - Social login (Google, Facebook, Instagram, Apple)
  - Email OTP verification
  - Mobile SMS OTP verification
- **Payment**: Stripe integration for payments
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time**: Shopping cart functionality
- **Admin Panel**: Product and order management
- **Landing Page**: Separate marketing landing page
- **Login-on-Demand**: Users only need to login when ordering

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Stripe** - Payment processing
- **MySQL Connector** - Database driver

### Database
- **MySQL 8.0** - Relational database
- **phpMyAdmin** - Database management interface

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- MySQL 8.0 or Docker
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ecommerce-app
```

### 2. Set Up the Database

#### Option A: Using Docker (Recommended)

```bash
cd database
docker-compose up -d
```

This will start:
- MySQL database on port 3306
- phpMyAdmin on port 8080

#### Option B: Manual MySQL Setup

1. Install MySQL 8.0
2. Create database: `CREATE DATABASE ecommerce_db;`
3. Update connection details in `backend/.env`

### 3. Set Up the Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Create tables and seed data
python seed_data.py

# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 4. Set Up the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

## 📚 API Documentation

The FastAPI backend automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user profile

#### Products
- `GET /api/products/` - List products
- `GET /api/products/{id}` - Get product details
- `GET /api/products/categories/` - List categories

#### Cart
- `GET /api/cart/` - Get cart items
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/{id}` - Update cart item
- `DELETE /api/cart/{id}` - Remove from cart

#### Orders
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}` - Get order details

## 🏗️ Project Structure

```
.
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── context/         # React contexts
│   │   └── lib/            # Utilities and API calls
│   └── package.json
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication utilities
│   ├── database.py         # Database configuration
│   ├── main.py             # FastAPI app
│   └── requirements.txt
├── database/               # Database setup
│   ├── docker-compose.yml  # Docker setup
│   └── init.sql            # Database initialization
└── README.md
```

## 🔑 Environment Variables

### Backend (.env)
```env
DATABASE_URL=mysql+mysqlconnector://root:rootpassword@localhost:3306/ecommerce_db
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 👥 Default Users

After running the seed script, you can login with:

- **Admin User**:
  - Username: `admin`
  - Password: `admin123`

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload

# Run tests (if available)
pytest

# Format code
black .
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🚀 Deployment

### Backend Deployment

1. Set up production database
2. Update environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run with production ASGI server: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`

### Frontend Deployment

1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or your preferred platform

## 🛡️ Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## 📱 Features Overview

### User Features
- User registration and authentication
- Product browsing and search
- Shopping cart management
- Order placement and tracking
- User profile management

### Admin Features
- Product management (CRUD)
- Category management
- Order management
- User management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.