from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Category schemas
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Product schemas
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    category_id: Optional[int] = None
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    image_url: Optional[str]
    category_id: Optional[int]
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse]

    class Config:
        from_attributes = True

# Cart schemas
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True

# Order schemas
class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str = "stripe"

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    shipping_address: str
    payment_method: str
    payment_status: str
    created_at: datetime
    order_items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# Payment schemas
class PaymentIntentCreate(BaseModel):
    amount: float  # in dollars