from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import get_password_hash

def create_sample_data():
    """Create sample data for development."""
    db = SessionLocal()
    
    try:
        # Create categories
        categories_data = [
            {"name": "Electronics", "description": "Electronic devices and gadgets"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Books", "description": "Books and literature"},
            {"name": "Home & Garden", "description": "Home improvement and gardening"},
            {"name": "Sports", "description": "Sports and fitness equipment"}
        ]
        
        for cat_data in categories_data:
            db_category = db.query(models.Category).filter(models.Category.name == cat_data["name"]).first()
            if not db_category:
                db_category = models.Category(**cat_data)
                db.add(db_category)
        
        db.commit()
        
        # Create admin user
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            admin_user = models.User(
                email="admin@ecommerce.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
        
        # Create sample products
        electronics_category = db.query(models.Category).filter(models.Category.name == "Electronics").first()
        clothing_category = db.query(models.Category).filter(models.Category.name == "Clothing").first()
        
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with advanced features",
                "price": 999.99,
                "stock_quantity": 50,
                "category_id": electronics_category.id if electronics_category else 1,
                "image_url": "/uploads/iphone15.jpg"
            },
            {
                "name": "MacBook Pro M3",
                "description": "Powerful laptop for professionals",
                "price": 1999.99,
                "stock_quantity": 25,
                "category_id": electronics_category.id if electronics_category else 1,
                "image_url": "/uploads/macbook.jpg"
            },
            {
                "name": "Nike Air Max",
                "description": "Comfortable running shoes",
                "price": 129.99,
                "stock_quantity": 100,
                "category_id": clothing_category.id if clothing_category else 2,
                "image_url": "/uploads/nike-airmax.jpg"
            },
            {
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones",
                "price": 199.99,
                "stock_quantity": 75,
                "category_id": electronics_category.id if electronics_category else 1,
                "image_url": "/uploads/headphones.jpg"
            }
        ]
        
        for prod_data in products_data:
            db_product = db.query(models.Product).filter(models.Product.name == prod_data["name"]).first()
            if not db_product:
                db_product = models.Product(**prod_data)
                db.add(db_product)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    # Create sample data
    create_sample_data()