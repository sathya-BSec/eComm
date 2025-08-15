'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { CartItem, cartAPI } from '@/lib/api';
import { useAuth } from './AuthContext';

interface CartContextType {
  items: CartItem[];
  addToCart: (productId: number, quantity: number) => Promise<void>;
  updateQuantity: (id: number, quantity: number) => Promise<void>;
  removeFromCart: (id: number) => Promise<void>;
  clearCart: () => void;
  totalItems: number;
  totalPrice: number;
  loading: boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = items.reduce((sum, item) => sum + item.quantity * item.product.price, 0);

  useEffect(() => {
    if (isAuthenticated) {
      loadCartItems();
    } else {
      setItems([]);
    }
  }, [isAuthenticated]);

  const loadCartItems = async () => {
    try {
      setLoading(true);
      const cartItems = await cartAPI.getCartItems();
      setItems(cartItems);
    } catch (error) {
      console.error('Failed to load cart items:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId: number, quantity: number) => {
    try {
      setLoading(true);
      const newItem = await cartAPI.addToCart(productId, quantity);
      
      // Check if item already exists
      const existingItemIndex = items.findIndex(item => item.product_id === productId);
      if (existingItemIndex > -1) {
        const updatedItems = [...items];
        updatedItems[existingItemIndex] = newItem;
        setItems(updatedItems);
      } else {
        setItems([...items, newItem]);
      }
    } catch (error) {
      console.error('Failed to add to cart:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (id: number, quantity: number) => {
    try {
      setLoading(true);
      const updatedItem = await cartAPI.updateCartItem(id, quantity);
      setItems(items.map(item => item.id === id ? updatedItem : item));
    } catch (error) {
      console.error('Failed to update cart item:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (id: number) => {
    try {
      setLoading(true);
      await cartAPI.removeFromCart(id);
      setItems(items.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to remove from cart:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearCart = () => {
    setItems([]);
  };

  const value: CartContextType = {
    items,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    totalItems,
    totalPrice,
    loading,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};