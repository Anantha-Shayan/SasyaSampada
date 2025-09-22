import React, { createContext, useContext, useState } from 'react';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    location: {
      state: '',
      district: '',
      market: ''
    },
    soilData: {
      N: 0,
      P: 0,
      K: 0,
      temperature: 0,
      humidity: 0,
      ph: 0,
      rainfall: 0
    },
    recommendations: [],
    weatherData: null,
    marketPrices: []
  });

  const updateLocation = (location) => {
    setUser(prev => ({
      ...prev,
      location: { ...prev.location, ...location }
    }));
  };

  const updateSoilData = (soilData) => {
    setUser(prev => ({
      ...prev,
      soilData: { ...prev.soilData, ...soilData }
    }));
  };

  const updateRecommendations = (recommendations) => {
    setUser(prev => ({
      ...prev,
      recommendations
    }));
  };

  const updateWeatherData = (weatherData) => {
    setUser(prev => ({
      ...prev,
      weatherData
    }));
  };

  const updateMarketPrices = (marketPrices) => {
    setUser(prev => ({
      ...prev,
      marketPrices
    }));
  };

  const value = {
    user,
    updateLocation,
    updateSoilData,
    updateRecommendations,
    updateWeatherData,
    updateMarketPrices
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};
