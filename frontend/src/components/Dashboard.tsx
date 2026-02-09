import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { ForecastService, CategoryForecast } from '../services/api';
import CategoryCard from './CategoryCard';
import ForecastChart from './ForecastChart';
import TopProducts from './TopProducts';

const Dashboard: React.FC = () => {
  const [timePeriod, setTimePeriod] = useState<string>('month');
  const [categories, setCategories] = useState<CategoryForecast[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const forecastService = new ForecastService();

  useEffect(() => {
    loadForecasts();
  }, [timePeriod]);

  const loadForecasts = async () => {
    setLoading(true);
    try {
      const data = await forecastService.getCategoryForecasts(timePeriod);
      setCategories(data);
      if (!selectedCategory && data.length > 0) {
        setSelectedCategory(data[0].category);
      }
    } catch (error) {
      console.error('Error loading forecasts:', error);
    }
    setLoading(false);
  };

  const handleTimePeriodChange = (period: string) => {
    setTimePeriod(period);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Sales Forecast Overview</h2>
        <div className="time-period-selector">
          {['week', 'month', 'year'].map((period) => (
            <button
              key={period}
              className={`period-btn ${timePeriod === period ? 'active' : ''}`}
              onClick={() => handleTimePeriodChange(period)}
            >
              {period.charAt(0).toUpperCase() + period.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading-section">
          <div className="spinner"></div>
          <p>Loading forecasts...</p>
        </div>
      ) : (
        <>
          <div className="categories-grid">
            {categories.map((category) => (
              <CategoryCard
                key={category.category}
                category={category}
                timePeriod={timePeriod}
                isSelected={selectedCategory === category.category}
                onSelect={() => setSelectedCategory(category.category)}
              />
            ))}
          </div>

          {selectedCategory && (
            <div className="detailed-view">
              <div className="chart-section">
                <ForecastChart
                  category={selectedCategory}
                  timePeriod={timePeriod}
                />
              </div>
              <div className="products-section">
                <TopProducts
                  category={selectedCategory}
                  timePeriod={timePeriod}
                />
              </div>
            </div>
          )}
        </>
      )}

      <div className="footer-info">
        <p>
          Powered by ensemble ML model (XGBoost + Prophet) | 
          Model Accuracy: 87% | 
          Last Updated: {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
