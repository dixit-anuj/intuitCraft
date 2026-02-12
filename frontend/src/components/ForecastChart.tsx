import React, { useEffect, useState, useCallback } from 'react';
import './ForecastChart.css';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { ForecastService, CategoryTrendResponse } from '../services/api';

const forecastService = new ForecastService();

interface ForecastChartProps {
  category: string;
  timePeriod: string;
}

const ForecastChart: React.FC<ForecastChartProps> = ({ category, timePeriod }) => {
  const [trendData, setTrendData] = useState<CategoryTrendResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadTrendData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await forecastService.getCategoryTrend(category, 60);
      setTrendData(data);
    } catch (error) {
      console.error('Error loading trend data:', error);
    }
    setLoading(false);
  }, [category]);

  useEffect(() => {
    loadTrendData();
  }, [loadTrendData]);

  if (loading) {
    return (
      <div className="chart-loading" role="status" aria-live="polite">
        <div className="spinner" aria-hidden="true"></div>
        <p>Loading chart...</p>
      </div>
    );
  }

  if (!trendData) {
    return (
      <div className="chart-error" role="alert">
        No data available
      </div>
    );
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

  // Build a screen reader summary
  const srSummary = `${category} sales chart. Historical average: ${Math.round(trendData.statistics.mean)} units. Range: ${Math.round(trendData.statistics.min)} to ${Math.round(trendData.statistics.max)}. Trend: ${trendData.statistics.trend || 'stable'}.`;

  return (
    <div className="forecast-chart" role="figure" aria-label={srSummary}>
      <div className="chart-header">
        <h3>{category} &mdash; Sales Trend & Forecast</h3>
        <div className="chart-legend" aria-hidden="true">
          <span className="legend-item">
            <span className="legend-swatch legend-actual"></span>
            Historical
          </span>
          <span className="legend-item">
            <span className="legend-swatch legend-forecast"></span>
            Forecast
          </span>
          <span className="legend-item">
            <span className="legend-swatch legend-confidence"></span>
            Confidence
          </span>
        </div>
      </div>

      {/* Screen-reader accessible data summary */}
      <p className="sr-only">{srSummary}</p>

      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey="date"
            stroke="var(--color-text-muted)"
            style={{ fontSize: '13px' }}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="var(--color-text-muted)"
            style={{ fontSize: '13px' }}
            tickFormatter={(value) => `${(value / 1000).toFixed(1)}k`}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              fontSize: '14px',
            }}
            formatter={(value: any) => [`${Math.round(value)} units`, '']}
          />
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#5A93FF"
            fillOpacity={0.12}
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#5A93FF"
            fillOpacity={0.12}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#236CFF"
            strokeWidth={2.5}
            dot={{ r: 2.5, fill: '#236CFF' }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#B25E02"
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={{ r: 2.5, fill: '#B25E02' }}
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="chart-stats">
        <div className="stat">
          <span className="stat-label">Average</span>
          <span className="stat-value">{Math.round(trendData.statistics.mean).toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Min</span>
          <span className="stat-value">{Math.round(trendData.statistics.min).toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Max</span>
          <span className="stat-value">{Math.round(trendData.statistics.max).toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Std Dev</span>
          <span className="stat-value">{Math.round(trendData.statistics.std).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;
