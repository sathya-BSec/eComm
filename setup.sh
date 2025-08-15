#!/bin/bash

# E-Commerce Application Setup Script
# This script sets up the entire e-commerce application

set -e  # Exit on any error

echo "🚀 Setting up E-Commerce Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    # Check Docker (optional)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. You'll need to set up MySQL manually."
    fi
    
    print_success "All requirements met!"
}

# Set up database
setup_database() {
    print_status "Setting up database..."
    
    if command -v docker &> /dev/null; then
        print_status "Starting MySQL with Docker..."
        cd database
        docker-compose up -d
        cd ..
        print_success "Database started with Docker!"
        print_status "phpMyAdmin available at: http://localhost:8080"
        print_status "Database credentials: root/rootpassword"
    else
        print_warning "Docker not available. Please set up MySQL manually:"
        print_warning "1. Install MySQL 8.0"
        print_warning "2. Create database: CREATE DATABASE ecommerce_db;"
        print_warning "3. Update backend/.env with your credentials"
    fi
}

# Set up backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set up environment file
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp .env.example .env
        print_warning "Please update backend/.env with your configuration!"
    fi
    
    cd ..
    print_success "Backend setup completed!"
}

# Set up frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f .env.local ]; then
        print_status "Creating frontend environment file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
    
    cd ..
    print_success "Frontend setup completed!"
}

# Initialize database data
init_database() {
    print_status "Initializing database with sample data..."
    
    cd backend
    source venv/bin/activate
    
    # Wait a bit for database to be ready
    if command -v docker &> /dev/null; then
        print_status "Waiting for database to be ready..."
        sleep 10
    fi
    
    # Run database initialization
    python seed_data.py
    
    cd ..
    print_success "Database initialized with sample data!"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 5
    
    # Start frontend
    print_status "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_success "Services started!"
    print_status "Backend API: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Frontend: http://localhost:3000"
    
    if command -v docker &> /dev/null; then
        print_status "phpMyAdmin: http://localhost:8080"
    fi
    
    print_status "Backend PID: $BACKEND_PID"
    print_status "Frontend PID: $FRONTEND_PID"
    
    echo ""
    print_success "🎉 E-Commerce application is running!"
    print_status "Default admin credentials:"
    print_status "Username: admin"
    print_status "Password: admin123"
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for user to stop
    trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
    wait
}

# Main setup flow
main() {
    echo "=================================="
    echo "E-Commerce Application Setup"
    echo "=================================="
    echo ""
    
    check_requirements
    echo ""
    
    setup_database
    echo ""
    
    setup_backend
    echo ""
    
    setup_frontend
    echo ""
    
    # Ask if user wants to initialize database
    read -p "Do you want to initialize the database with sample data? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_database
        echo ""
    fi
    
    # Ask if user wants to start services
    read -p "Do you want to start the application now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
    else
        print_success "Setup completed!"
        print_status "To start the application later, run:"
        print_status "  Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
        print_status "  Frontend: cd frontend && npm run dev"
    fi
}

# Run main function
main "$@"