from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import stripe
import os

from database import get_db
import models
import schemas
from auth import get_current_active_user, get_admin_user

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()

@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user."""
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific order."""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    order_data: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart items."""
    # Get cart items
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total_amount = 0
    order_items_data = []
    
    for cart_item in cart_items:
        product = cart_item.product
        if not product.is_active:
            raise HTTPException(
                status_code=400, 
                detail=f"Product {product.name} is no longer available"
            )
        
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )
        
        item_total = product.price * cart_item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "price": product.price
        })
    
    # Create order
    db_order = models.Order(
        user_id=current_user.id,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        payment_method=order_data.payment_method
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items and update stock
    for item_data in order_items_data:
        order_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(order_item)
        
        # Update product stock
        product = db.query(models.Product).filter(
            models.Product.id == item_data["product_id"]
        ).first()
        product.stock_quantity -= item_data["quantity"]
    
    # Clear cart
    db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).delete()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.post("/create-payment-intent")
def create_payment_intent(
    payment_data: schemas.PaymentIntentCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a Stripe payment intent."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment_data.amount * 100),  # Stripe uses cents
            currency='usd',
            metadata={
                'user_id': current_user.id,
                'user_email': current_user.email
            }
        )
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/confirm-payment")
def confirm_payment(
    order_id: int,
    payment_intent_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm payment for an order."""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == "succeeded":
            order.payment_status = "paid"
            order.status = "paid"
            order.stripe_payment_intent_id = payment_intent_id
            db.commit()
            
            return {"message": "Payment confirmed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Payment not completed")
            
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Admin endpoints
@router.get("/admin/all", response_model=List[schemas.OrderResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)."""
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_user: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)."""
    valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    
    return {"message": f"Order status updated to {status}"}