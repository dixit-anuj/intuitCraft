import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface ProductForecast {
  product_id: string;
  product_name: string;
  category: string;
  predicted_sales: number;
  predicted_revenue: number;
  confidence_lower?: number;
  confidence_upper?: number;
  trend: string;
  change_percent: number;
}

export interface CategoryForecast {
  category: string;
  total_predicted_sales: number;
  total_predicted_revenue: number;
  top_products: ProductForecast[];
  trend: string;
  growth_rate: number;
}

export interface TrendDataPoint {
  date: string;
  actual_sales?: number;
  predicted_sales?: number;
  confidence_lower?: number;
  confidence_upper?: number;
}

export interface CategoryTrendResponse {
  category: string;
  historical_data: TrendDataPoint[];
  forecast_data: TrendDataPoint[];
  statistics: {
    mean: number;
    std: number;
    min: number;
    max: number;
    trend: string;
  };
}

export class ForecastService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getTopProducts(
    timePeriod: string,
    category?: string,
    limit: number = 10
  ): Promise<ProductForecast[]> {
    const params: any = { time_period: timePeriod, limit };
    if (category) {
      params.category = category;
    }
    
    const response = await this.client.get('/forecast/top-products', { params });
    return response.data.products;
  }

  async getCategoryForecasts(timePeriod: string): Promise<CategoryForecast[]> {
    const response = await this.client.get('/forecast/categories', {
      params: { time_period: timePeriod },
    });
    return response.data;
  }

  async getCategoryTrend(
    category: string,
    days: number = 90
  ): Promise<CategoryTrendResponse> {
    const response = await this.client.get(`/forecast/trends/${category}`, {
      params: { days },
    });
    return response.data;
  }

  async getAvailableCategories(): Promise<string[]> {
    const response = await this.client.get('/data/categories');
    return response.data.categories;
  }

  async getModelInfo(): Promise<any> {
    const response = await this.client.get('/forecast/model-info');
    return response.data;
  }
}
