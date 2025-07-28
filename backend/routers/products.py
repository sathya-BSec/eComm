from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from uuid import uuid4

from database import get_db
import models
import schemas
from auth import get_current_active_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering."""
    query = db.query(models.Product).filter(models.Product.is_active == True)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if search:
        query = query.filter(models.Product.name.contains(search))
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.post("/", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Create a new product (admin only)."""
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Update a product (admin only)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Delete a product (admin only)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete
    db_product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/upload-image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Upload an image for a product (admin only)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update product image URL
    db_product.image_url = f"/uploads/{unique_filename}"
    db.commit()
    
    return {"message": "Image uploaded successfully", "image_url": db_product.image_url}

# Categories
@router.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    categories = db.query(models.Category).all()
    return categories

@router.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Create a new category (admin only)."""
    # Check if category already exists
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category