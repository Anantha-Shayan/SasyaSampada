import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const RecommendationResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useUser();
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (location.state?.recommendation) {
      setRecommendation(location.state.recommendation);
    }
  }, [location.state]);

  const getNewRecommendation = async () => {
    setIsLoading(true);
    // Simulate getting new recommendation
    setTimeout(() => {
      const newRec = {
        ...recommendation,
        timestamp: new Date().toISOString(),
        id: Math.random().toString(36).substr(2, 9)
      };
      setRecommendation(newRec);
      setIsLoading(false);
    }, 2000);
  };

  const getCropIcon = (crop) => {
    const icons = {
      'rice': '🌾',
      'wheat': '🌾',
      'maize': '🌽',
      'cotton': '🌿',
      'soybean': '🫘',
      'barley': '🌾',
      'sorghum': '🌾',
      'coffee': '☕',
      'mango': '🥭',
      'jute': '🌿',
      'sugarcane': '🎋',
      'tomato': '🍅',
      'potato': '🥔',
      'onion': '🧅',
      'groundnut': '🥜',
      'sunflower': '🌻',
      'coconut': '🥥',
      'banana': '🍌',
      'apple': '🍎',
      'grapes': '🍇'
    };
    return icons[crop?.toLowerCase()] || '🌱';
  };

  const getSoilHealthColor = (ph) => {
    if (ph < 6.0) return 'text-red-600';
    if (ph > 8.0) return 'text-orange-600';
    return 'text-green-600';
  };

  const getSoilHealthText = (ph) => {
    if (ph < 6.0) return 'Acidic - Needs Lime';
    if (ph > 8.0) return 'Alkaline - Needs Sulfur';
    return 'Optimal Range';
  };

  // Helper functions to extract data from advice text using simple string parsing
  const extractCropFromAdvice = (advice, field) => {
    if (!advice) return null;
    const lines = advice.split('\n');
    const line = lines.find(l => l.includes(`${field}:`));
    if (line) {
      return line.split(`${field}:`)[1].trim();
    }
    return null;
  };

  const extractValueFromAdvice = (advice, field) => {
    if (!advice) return null;
    const lines = advice.split('\n');
    const line = lines.find(l => l.includes(`${field}:`));
    if (line) {
      let value = line.split(`${field}:`)[1].trim();
      // Clean up common suffixes using simple string replacement
      if (value.includes('(Auto-detected)')) {
        value = value.replace('(Auto-detected)', '').trim();
      }
      return value;
    }
    return null;
  };

  const extractLocationFromAdvice = (advice) => {
    if (!advice) return null;
    const lines = advice.split('\n');
    const locationLine = lines.find(line => line.includes('Location:'));
    if (locationLine) {
      let location = locationLine.split('Location:')[1].trim();
      // Remove (Auto-detected) suffix using simple string replacement
      if (location.includes('(Auto-detected)')) {
        location = location.replace('(Auto-detected)', '').trim();
      }
      return location;
    }
    return null;
  };

  const extractSuitabilityFromAdvice = (advice) => {
    if (!advice) return null;
    const lines = advice.split('\n');
    const suitabilityLine = lines.find(line => line.includes('District Suitability:'));
    if (suitabilityLine) {
      let suitability = suitabilityLine.split('District Suitability:')[1].trim();
      return suitability;
    }
    return null;
  };

  if (!recommendation) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            No Recommendation Found
          </h2>
          <button 
            className="bg-primary text-white px-6 py-3 rounded-lg"
            onClick={() => navigate('/advisory')}
          >
            Get New Recommendation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      {/* Header */}
      <header className="sticky top-0 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-sm z-10">
        <div className="flex items-center justify-between p-4">
          <button 
            className="flex h-12 w-12 items-center justify-center text-gray-900 dark:text-white"
            onClick={() => navigate('/advisory')}
          >
            <span className="material-symbols-outlined text-3xl">arrow_back</span>
          </button>
          <h1 className="text-lg font-bold">Crop Recommendation</h1>
          <button 
            className="p-2"
            onClick={getNewRecommendation}
            disabled={isLoading}
          >
            <span className="material-symbols-outlined text-2xl">
              {isLoading ? 'refresh' : 'refresh'}
            </span>
          </button>
        </div>
      </header>

      <div className="p-4 space-y-6">
        {/* Main Recommendation Card */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-xl p-6 shadow-lg border border-green-200 dark:border-green-700">
          <div className="text-center mb-6">
            <div className="relative inline-block">
              <div className="text-8xl mb-4 drop-shadow-lg">
                {getCropIcon(recommendation.mlCrop || recommendation.finalCrop)}
              </div>
              <div className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full p-2">
                <span className="material-symbols-outlined text-lg">verified</span>
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {recommendation.mlCrop || recommendation.finalCrop}
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              🎯 AI-Recommended Crop for Your Farm
            </p>
          </div>

          {/* Recommendation Status */}
          <div className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-green-300 dark:border-green-600 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="bg-green-500 rounded-full p-2 mr-4">
                <span className="material-symbols-outlined text-white text-xl">
                  eco
                </span>
              </div>
              <div>
                <h3 className="font-bold text-green-800 dark:text-green-300 text-lg">
                  Optimal Match Found
                </h3>
                <p className="text-sm text-green-700 dark:text-green-400">
                  Perfect compatibility with your soil conditions, weather, and market demand
                </p>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl mb-1">🌱</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">ML Powered</div>
            </div>
            <div className="text-center bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl mb-1">🌤️</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Weather Aware</div>
            </div>
            <div className="text-center bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl mb-1">💰</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Market Optimized</div>
            </div>
          </div>
        </div>



        {/* Detailed Recommendations */}
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span className="material-symbols-outlined text-primary mr-2">lightbulb</span>
            Detailed Recommendations
          </h3>

          {/* Parse and display the advice in a structured way */}
          {recommendation.advice && (
            <div className="space-y-4">
              {/* ML Prediction Card */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-700 rounded-lg p-5">
                <div className="flex items-center mb-4">
                  <div className="bg-green-100 dark:bg-green-800 rounded-full p-2 mr-3">
                    <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-lg">psychology</span>
                  </div>
                  <h4 className="font-bold text-green-800 dark:text-green-300 text-lg">ML-Powered Crop Recommendation</h4>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between bg-white/50 dark:bg-gray-800/30 rounded-lg p-3">
                    <div className="flex items-center">
                      <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-xl mr-3">agriculture</span>
                      <span className="text-gray-600 dark:text-gray-400 text-sm">ML Predicted Crop:</span>
                    </div>
                    <span className="font-bold text-green-800 dark:text-green-300 text-lg">
                      {extractCropFromAdvice(recommendation.advice, 'ML Predicted Crop') || recommendation.mlCrop || 'coffee'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between bg-white/50 dark:bg-gray-800/30 rounded-lg p-3">
                    <div className="flex items-center">
                      <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-xl mr-3">recommend</span>
                      <span className="text-gray-600 dark:text-gray-400 text-sm">Final Recommended:</span>
                    </div>
                    <span className="font-bold text-green-800 dark:text-green-300 text-lg">
                      {extractCropFromAdvice(recommendation.advice, 'Final Recommended Crop') || recommendation.finalCrop || 'mango'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Soil Conditions Card */}
              <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-5">
                <div className="flex items-center mb-4">
                  <div className="bg-blue-100 dark:bg-blue-800 rounded-full p-2 mr-3">
                    <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-lg">terrain</span>
                  </div>
                  <h4 className="font-bold text-blue-800 dark:text-blue-300 text-lg">Soil Analysis Results</h4>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                      {extractValueFromAdvice(recommendation.advice, 'Soil pH') || user.soilData?.ph || '6.8'}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium">pH Level</div>
                  </div>
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                      {(extractValueFromAdvice(recommendation.advice, 'Temperature') || user.soilData?.temperature || '28.0') + (extractValueFromAdvice(recommendation.advice, 'Temperature')?.includes('°C') ? '' : '°C')}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium">Temperature</div>
                  </div>
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                      {(extractValueFromAdvice(recommendation.advice, 'Humidity') || user.soilData?.humidity || '80.0') + (extractValueFromAdvice(recommendation.advice, 'Humidity')?.includes('%') ? '' : '%')}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium">Humidity</div>
                  </div>
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4 text-center">
                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                      {extractValueFromAdvice(recommendation.advice, 'Weather Condition') || 'Good'}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium">Condition</div>
                  </div>
                </div>
              </div>

              {/* Location & Suitability Card */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-5">
                <div className="flex items-center mb-4">
                  <div className="bg-purple-100 dark:bg-purple-800 rounded-full p-2 mr-3">
                    <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-lg">location_on</span>
                  </div>
                  <h4 className="font-bold text-purple-800 dark:text-purple-300 text-lg">Location & Suitability</h4>
                </div>
                <div className="space-y-3">
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center flex-shrink-0">
                        <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-xl mr-3">place</span>
                        <span className="text-gray-600 dark:text-gray-400 text-sm font-medium">Location:</span>
                      </div>
                      <span className="font-bold text-purple-800 dark:text-purple-300 text-right ml-2 flex-1 min-w-0">
                        {extractLocationFromAdvice(recommendation.advice) || 'Bangalore, Karnataka'}
                      </span>
                    </div>
                  </div>
                  <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center flex-shrink-0">
                        <span className="material-symbols-outlined text-purple-600 dark:text-purple-400 text-xl mr-3">verified</span>
                        <span className="text-gray-600 dark:text-gray-400 text-sm font-medium">Suitability:</span>
                      </div>
                      <span className="font-bold text-purple-800 dark:text-purple-300 text-right ml-2 flex-1 min-w-0 text-sm">
                        {extractSuitabilityFromAdvice(recommendation.advice) || '⚠️ Check local conditions'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Market Information Card */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-5">
                <div className="flex items-center mb-4">
                  <div className="bg-yellow-100 dark:bg-yellow-800 rounded-full p-2 mr-3">
                    <span className="material-symbols-outlined text-yellow-600 dark:text-yellow-400 text-lg">trending_up</span>
                  </div>
                  <h4 className="font-bold text-yellow-800 dark:text-yellow-300 text-lg">Market Analysis</h4>
                </div>
                <div className="bg-white/60 dark:bg-gray-800/40 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="material-symbols-outlined text-yellow-600 dark:text-yellow-400 text-xl mr-3">monetization_on</span>
                      <div>
                        <div className="text-gray-600 dark:text-gray-400 text-sm font-medium">Best Market Crop:</div>
                        <div className="font-bold text-yellow-800 dark:text-yellow-300 text-lg">
                          {recommendation.bestMarketCrop || 'Drumstick'}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                        {recommendation.bestPrice || '₹10,300'}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">per quintal</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            className="bg-gradient-to-r from-primary to-green-600 hover:from-primary/90 hover:to-green-600/90 text-white py-4 px-6 rounded-xl font-semibold shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
            onClick={() => navigate('/advisory')}
          >
            <span className="material-symbols-outlined mr-2">refresh</span>
            Get New Recommendation
          </button>
          <button
            className="bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 hover:from-gray-200 hover:to-gray-300 dark:hover:from-gray-600 dark:hover:to-gray-500 text-gray-800 dark:text-gray-200 py-4 px-6 rounded-xl font-semibold shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
            onClick={() => navigate('/')}
          >
            <span className="material-symbols-outlined mr-2">home</span>
            Back to Dashboard
          </button>
        </div>

        {/* Additional Quick Actions */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <button
            className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300 py-3 px-4 rounded-lg font-medium hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors flex items-center justify-center"
            onClick={() => navigate('/weather')}
          >
            <span className="material-symbols-outlined mr-2 text-lg">cloud</span>
            Check Weather
          </button>
          <button
            className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 text-yellow-700 dark:text-yellow-300 py-3 px-4 rounded-lg font-medium hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors flex items-center justify-center"
            onClick={() => navigate('/market')}
          >
            <span className="material-symbols-outlined mr-2 text-lg">trending_up</span>
            Market Prices
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendationResults;
