import React, { useEffect, useState, useCallback } from 'react';
import './TopProducts.css';
import { ForecastService, ProductForecast } from '../services/api';

const forecastService = new ForecastService();

interface TopProductsProps {
  category: string;
  timePeriod: string;
}

const TopProducts: React.FC<TopProductsProps> = ({ category, timePeriod }) => {
  const [products, setProducts] = useState<ProductForecast[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await forecastService.getTopProducts(timePeriod, category, 8);
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    }
    setLoading(false);
  }, [category, timePeriod]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

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

  const getTrendArrow = (trend: string): string => {
    if (trend === 'increasing') return '\u2197';
    if (trend === 'decreasing') return '\u2198';
    return '\u2192';
  };

  const getTrendClass = (trend: string): string => {
    if (trend === 'increasing') return 'trend-up';
    if (trend === 'decreasing') return 'trend-down';
    return 'trend-stable';
  };

  const getTrendLabel = (trend: string): string => {
    if (trend === 'increasing') return 'Up';
    if (trend === 'decreasing') return 'Down';
    return 'Stable';
  };

  if (loading) {
    return (
      <div className="top-products">
        <h3>Top Products</h3>
        <div className="products-loading" role="status" aria-live="polite">
          <div className="spinner" aria-hidden="true"></div>
          <p>Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="top-products">
      <h3>Top Products in {category}</h3>
      <ol className="products-list" aria-label={`Top products in ${category}`}>
        {products.map((product, index) => (
          <li key={product.product_id} className="product-item">
            <div className="product-rank" aria-hidden="true">
              {index + 1}
            </div>
            <div className="product-info">
              <div className="product-name">{product.product_name}</div>
              <div className="product-stats">
                <span className="product-sales">
                  {formatNumber(product.predicted_sales)} units
                </span>
                <span className="product-divider" aria-hidden="true">&middot;</span>
                <span className="product-revenue">
                  {formatCurrency(product.predicted_revenue)}
                </span>
              </div>
              <div
                className={`product-trend ${getTrendClass(product.trend)}`}
                aria-label={`${getTrendLabel(product.trend)} ${Math.abs(product.change_percent).toFixed(1)} percent`}
              >
                <span aria-hidden="true">{getTrendArrow(product.trend)}</span>
                {product.change_percent > 0 ? '+' : ''}{product.change_percent.toFixed(1)}%
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
};

export default TopProducts;
