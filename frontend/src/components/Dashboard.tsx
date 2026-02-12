import React, { useState, useEffect, useCallback, useRef } from 'react';
import './Dashboard.css';
import { ForecastService, CategoryForecast, ModelInfo } from '../services/api';
import CategoryCard from './CategoryCard';
import ForecastChart from './ForecastChart';
import TopProducts from './TopProducts';

const forecastService = new ForecastService();

const Dashboard: React.FC = () => {
  const [timePeriod, setTimePeriod] = useState<string>('month');
  const [categories, setCategories] = useState<CategoryForecast[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const selectedRef = useRef(selectedCategory);
  selectedRef.current = selectedCategory;

  const loadForecasts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await forecastService.getCategoryForecasts(timePeriod);
      setCategories(data);
      if (!selectedRef.current && data.length > 0) {
        setSelectedCategory(data[0].category);
      }
    } catch (error) {
      console.error('Error loading forecasts:', error);
    }
    setLoading(false);
  }, [timePeriod]);

  useEffect(() => {
    loadForecasts();
  }, [loadForecasts]);

  useEffect(() => {
    forecastService.getModelInfo()
      .then(info => setModelInfo(info))
      .catch(err => console.error('Error loading model info:', err));
  }, []);

  const handleTimePeriodChange = (period: string) => {
    setTimePeriod(period);
  };

  return (
    <main id="main-content" className="dashboard" role="main">
      <div className="dashboard-header">
        <h2>Sales Forecast Overview</h2>
        <nav aria-label="Time period selection" className="time-period-selector">
          {['week', 'month', 'year'].map((period) => (
            <button
              key={period}
              className={`period-btn ${timePeriod === period ? 'active' : ''}`}
              onClick={() => handleTimePeriodChange(period)}
              aria-pressed={timePeriod === period}
              aria-label={`Show ${period}ly forecast`}
            >
              {period.charAt(0).toUpperCase() + period.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {loading ? (
        <div className="loading-section" role="status" aria-live="polite">
          <div className="spinner" aria-hidden="true"></div>
          <p>Loading forecasts...</p>
        </div>
      ) : (
        <>
          <section aria-label="Category forecasts">
            <h3 className="sr-only">Category Cards</h3>
            <div className="categories-grid" role="list">
              {categories.map((category) => (
                <div role="listitem" key={category.category}>
                  <CategoryCard
                    category={category}
                    timePeriod={timePeriod}
                    isSelected={selectedCategory === category.category}
                    onSelect={() => setSelectedCategory(category.category)}
                  />
                </div>
              ))}
            </div>
          </section>

          {selectedCategory && (
            <section
              className="detailed-view"
              aria-label={`Detailed forecast for ${selectedCategory}`}
              aria-live="polite"
            >
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
            </section>
          )}
        </>
      )}

      <footer className="footer-info" role="contentinfo">
        <p>
          Powered by {modelInfo ? modelInfo.model_type : 'ensemble ML model'} v{modelInfo ? modelInfo.version : '...'} |
          Model Accuracy: {modelInfo ? `${Math.round(modelInfo.performance.holdout_r2 * 100)}% R²` : 'Loading...'} |
          Features: {modelInfo ? modelInfo.num_features : '...'} |
          Last Updated: {new Date().toLocaleDateString()}
        </p>
      </footer>
    </main>
  );
};

export default Dashboard;
