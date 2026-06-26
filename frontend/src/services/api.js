import axios from 'axios';

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const advisoryAPI = {
  getCropAdvisory: async (soilData, location) => {
    try {
      const response = await api.post('/api/advisory', {
        soil_data: soilData,
        location: location
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get crop advisory');
    }
  }
};

export const weatherAPI = {
  getWeather: async (city) => {
    try {
      const response = await api.post('/api/weather', { city });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get weather data');
    }
  }
};

export const marketAPI = {
  getMarketPrices: async (state, district, market, date = null) => {
    try {
      const response = await api.post('/api/market-prices', {
        state,
        district,
        market,
        date
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get market prices');
    }
  }
};

export const chatAPI = {
  sendMessage: async (question, sessionId = 'default') => {
    try {
      const response = await api.post('/api/chat', {
        question,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  }
};

export const dataAPI = {
  getDistrictCrops: async (state, district) => {
    try {
      const response = await api.get(`/api/district-crops/${state}/${district}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get district crops');
    }
  },
  
  getCropDistricts: async (crop) => {
    try {
      const response = await api.get(`/api/crop-districts/${crop}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get crop districts');
    }
  },
  
  getAllCrops: async () => {
    try {
      const response = await api.get('/api/crops');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get crops');
    }
  },
  
  getAllDistricts: async () => {
    try {
      const response = await api.get('/api/districts');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get districts');
    }
  }
};

export default api;
