import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock_quantity: number;
  category_id: number;
  image_url: string;
  is_active: boolean;
  created_at: string;
  category: Category;
}

export interface Category {
  id: number;
  name: string;
  description: string;
}

export interface CartItem {
  id: number;
  product_id: number;
  user_id: number;
  quantity: number;
  product: Product;
}

export interface Order {
  id: number;
  user_id: number;
  total_amount: number;
  status: string;
  payment_status: string;
  shipping_address: string;
  created_at: string;
  items: OrderItem[];
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price: number;
  product: Product;
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// Products API
export const productsAPI = {
  getProducts: async (params?: {
    skip?: number;
    limit?: number;
    category_id?: number;
    search?: string;
  }): Promise<Product[]> => {
    const response = await api.get('/api/products/', { params });
    return response.data;
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/api/products/${id}`);
    return response.data;
  },

  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/api/products/categories/');
    return response.data;
  },
};

// Cart API
export const cartAPI = {
  getCartItems: async (): Promise<CartItem[]> => {
    const response = await api.get('/api/cart/');
    return response.data;
  },

  addToCart: async (product_id: number, quantity: number): Promise<CartItem> => {
    const response = await api.post('/api/cart/', { product_id, quantity });
    return response.data;
  },

  updateCartItem: async (id: number, quantity: number): Promise<CartItem> => {
    const response = await api.put(`/api/cart/${id}`, { quantity });
    return response.data;
  },

  removeFromCart: async (id: number): Promise<void> => {
    await api.delete(`/api/cart/${id}`);
  },
};

// Orders API
export const ordersAPI = {
  getOrders: async (): Promise<Order[]> => {
    const response = await api.get('/api/orders/');
    return response.data;
  },

  createOrder: async (shipping_address: string): Promise<Order> => {
    const response = await api.post('/api/orders/', { shipping_address });
    return response.data;
  },

  getOrder: async (id: number): Promise<Order> => {
    const response = await api.get(`/api/orders/${id}`);
    return response.data;
  },
};

export default api;