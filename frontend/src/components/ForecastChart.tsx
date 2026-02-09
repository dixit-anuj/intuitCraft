import React, { useEffect, useState } from 'react';
import './ForecastChart.css';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { ForecastService, CategoryTrendResponse } from '../services/api';

interface ForecastChartProps {
  category: string;
  timePeriod: string;
}

const ForecastChart: React.FC<ForecastChartProps> = ({ category, timePeriod }) => {
  const [trendData, setTrendData] = useState<CategoryTrendResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const forecastService = new ForecastService();

  useEffect(() => {
    loadTrendData();
  }, [category]);

  const loadTrendData = async () => {
    setLoading(true);
    try {
      const data = await forecastService.getCategoryTrend(category, 60);
      setTrendData(data);
    } catch (error) {
      console.error('Error loading trend data:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="chart-loading">
        <div className="spinner"></div>
        <p>Loading chart...</p>
      </div>
    );
  }

  if (!trendData) {
    return <div className="chart-error">No data available</div>;
  }

  // Combine historical and forecast data
  const chartData = [
    ...trendData.historical_data.slice(-30).map(d => ({
      date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      actual: d.actual_sales,
      predicted: null,
      lower: null,
      upper: null,
    })),
    ...trendData.forecast_data.map(d => ({
      date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      actual: null,
      predicted: d.predicted_sales,
      lower: d.confidence_lower,
      upper: d.confidence_upper,
    })),
  ];

  return (
    <div className="forecast-chart">
      <div className="chart-header">
        <h3>{category} - Sales Trend & Forecast</h3>
        <div className="chart-legend">
          <span className="legend-item">
            <span className="legend-dot actual"></span>
            Historical
          </span>
          <span className="legend-item">
            <span className="legend-dot forecast"></span>
            Forecast
          </span>
          <span className="legend-item">
            <span className="legend-dot confidence"></span>
            Confidence Range
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            stroke="#718096"
            style={{ fontSize: '12px' }}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#718096"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            }}
            formatter={(value: any) => [`${Math.round(value)} units`, '']}
          />
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#667eea"
            fillOpacity={0.1}
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#667eea"
            fillOpacity={0.1}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#667eea"
            strokeWidth={2}
            dot={{ r: 3 }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="chart-stats">
        <div className="stat">
          <span className="stat-label">Average</span>
          <span className="stat-value">{Math.round(trendData.statistics.mean)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Min</span>
          <span className="stat-value">{Math.round(trendData.statistics.min)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Max</span>
          <span className="stat-value">{Math.round(trendData.statistics.max)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Std Dev</span>
          <span className="stat-value">{Math.round(trendData.statistics.std)}</span>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;
