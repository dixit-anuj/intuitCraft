import React from 'react';
import './CategoryCard.css';
import { CategoryForecast } from '../services/api';

interface CategoryCardProps {
  category: CategoryForecast;
  timePeriod: string;
  isSelected: boolean;
  onSelect: () => void;
}

const CategoryCard: React.FC<CategoryCardProps> = ({
  category,
  timePeriod,
  isSelected,
  onSelect,
}) => {
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

  const getTrendLabel = (trend: string): string => {
    if (trend === 'increasing') return 'Up';
    if (trend === 'decreasing') return 'Down';
    return 'Stable';
  };

  const getTrendClass = (trend: string): string => {
    if (trend === 'increasing') return 'trend-up';
    if (trend === 'decreasing') return 'trend-down';
    return 'trend-stable';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect();
    }
  };

  return (
    <div
      className={`category-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-pressed={isSelected}
      aria-label={`${category.category}: ${formatNumber(category.total_predicted_sales)} predicted sales, ${getTrendLabel(category.trend)} ${Math.abs(category.growth_rate).toFixed(1)} percent`}
    >
      <div className="card-header">
        <h3>{category.category}</h3>
        <span className={`trend-badge ${getTrendClass(category.trend)}`}>
          <span className="trend-arrow" aria-hidden="true">
            {category.trend === 'increasing' ? '\u2197' : category.trend === 'decreasing' ? '\u2198' : '\u2192'}
          </span>
          {category.growth_rate > 0 ? '+' : ''}{category.growth_rate.toFixed(1)}%
        </span>
      </div>

      <div className="card-metrics">
        <div className="metric">
          <span className="metric-label">Predicted Sales</span>
          <span className="metric-value">{formatNumber(category.total_predicted_sales)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Predicted Revenue</span>
          <span className="metric-value">{formatCurrency(category.total_predicted_revenue)}</span>
        </div>
      </div>

      <div className="card-footer">
        <span className="top-product">
          Top: {category.top_products[0]?.product_name || 'N/A'}
        </span>
      </div>
    </div>
  );
};

export default CategoryCard;
