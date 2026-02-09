import React, { useEffect, useState } from 'react';
import './TopProducts.css';
import { ForecastService, ProductForecast } from '../services/api';

interface TopProductsProps {
  category: string;
  timePeriod: string;
}

const TopProducts: React.FC<TopProductsProps> = ({ category, timePeriod }) => {
  const [products, setProducts] = useState<ProductForecast[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const forecastService = new ForecastService();

  useEffect(() => {
    loadProducts();
  }, [category, timePeriod]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await forecastService.getTopProducts(timePeriod, category, 8);
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    }
    setLoading(false);
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getTrendIcon = (trend: string): string => {
    if (trend === 'increasing') return '↗';
    if (trend === 'decreasing') return '↘';
    return '→';
  };

  const getTrendColor = (trend: string): string => {
    if (trend === 'increasing') return '#10b981';
    if (trend === 'decreasing') return '#ef4444';
    return '#6b7280';
  };

  if (loading) {
    return (
      <div className="top-products">
        <h3>Top Products</h3>
        <div className="products-loading">
          <div className="spinner"></div>
          <p>Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="top-products">
      <h3>Top Products in {category}</h3>
      <div className="products-list">
        {products.map((product, index) => (
          <div key={product.product_id} className="product-item">
            <div className="product-rank">#{index + 1}</div>
            <div className="product-info">
              <div className="product-name">{product.product_name}</div>
              <div className="product-stats">
                <span className="product-sales">
                  {formatNumber(product.predicted_sales)} units
                </span>
                <span className="product-revenue">
                  {formatCurrency(product.predicted_revenue)}
                </span>
              </div>
              <div className="product-trend" style={{ color: getTrendColor(product.trend) }}>
                {getTrendIcon(product.trend)} {product.change_percent > 0 ? '+' : ''}{product.change_percent.toFixed(1)}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopProducts;
