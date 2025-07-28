from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.CartItemResponse])
def get_cart_items(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all cart items for the current user."""
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()
    return cart_items

@router.post("/", response_model=schemas.CartItemResponse)
def add_to_cart(
    cart_item: schemas.CartItemCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an item to the cart."""
    # Check if product exists
    product = db.query(models.Product).filter(
        models.Product.id == cart_item.product_id,
        models.Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == cart_item.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        db_cart_item = models.CartItem(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

@router.put("/{cart_item_id}", response_model=schemas.CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    cart_item_update: schemas.CartItemUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity."""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if cart_item_update.quantity <= 0:
        # Remove item if quantity is 0 or less
        db.delete(cart_item)
        db.commit()
        return {"message": "Item removed from cart"}
    
    cart_item.quantity = cart_item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove an item from the cart."""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/")
def clear_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear all items from the cart."""
    db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "Cart cleared"}