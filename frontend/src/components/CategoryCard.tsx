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

  const getTrendIcon = (trend: string): string => {
    if (trend === 'increasing') return '📈';
    if (trend === 'decreasing') return '📉';
    return '➡️';
  };

  const getTrendColor = (trend: string): string => {
    if (trend === 'increasing') return '#10b981';
    if (trend === 'decreasing') return '#ef4444';
    return '#6b7280';
  };

  return (
    <div
      className={`category-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="card-header">
        <h3>{category.category}</h3>
        <span className="trend-badge" style={{ background: getTrendColor(category.trend) + '20', color: getTrendColor(category.trend) }}>
          {getTrendIcon(category.trend)} {category.growth_rate > 0 ? '+' : ''}{category.growth_rate.toFixed(1)}%
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
