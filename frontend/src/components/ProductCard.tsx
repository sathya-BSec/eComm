'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ShoppingCart, Plus } from 'lucide-react';
import { Product } from '@/lib/api';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const [adding, setAdding] = useState(false);
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!isAuthenticated) {
      // Redirect to login or show message
      return;
    }

    try {
      setAdding(true);
      await addToCart(product.id, 1);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setAdding(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  return (
    <Link href={`/products/${product.id}`}>
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 group">
        {/* Product Image */}
        <div className="relative h-48 bg-gray-200 overflow-hidden">
          {product.image_url ? (
            <Image
              src={product.image_url}
              alt={product.name}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                // Fallback to placeholder if image fails to load
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y3ZjdmNyIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD4KPC9zdmc+';
              }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-2 bg-gray-300 rounded-full flex items-center justify-center">
                  <Image 
                    src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIxIDEyVjdIMTZMMTQgNUgxMEw4IDdIM1Y5SDIxVjEyWiIgZmlsbD0iIzk5OTk5OSIvPgo8Y2lyY2xlIGN4PSIxMiIgY3k9IjEzIiByPSIzIiBmaWxsPSIjOTk5OTk5Ii8+Cjwvc3ZnPgo="
                    alt="No image"
                    width={24}
                    height={24}
                  />
                </div>
                <span className="text-sm">No Image</span>
              </div>
            </div>
          )}
          
          {/* Stock Badge */}
          {product.stock_quantity === 0 && (
            <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-semibold">
              Out of Stock
            </div>
          )}
          
          {product.stock_quantity > 0 && product.stock_quantity <= 10 && (
            <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-semibold">
              Low Stock
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
            {product.name}
          </h3>
          
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {product.description}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-xl font-bold text-gray-900">
                {formatPrice(product.price)}
              </span>
              <span className="text-xs text-gray-500">
                {product.stock_quantity} in stock
              </span>
            </div>

            {isAuthenticated && product.stock_quantity > 0 && (
              <button
                onClick={handleAddToCart}
                disabled={adding}
                className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Add to cart"
              >
                {adding ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <ShoppingCart className="w-5 h-5" />
                )}
              </button>
            )}
          </div>

          {/* Category */}
          {product.category && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">
                {product.category.name}
              </span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;