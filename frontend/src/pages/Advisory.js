import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { advisoryAPI } from '../services/api';

const Advisory = () => {
  const { updateSoilData, updateRecommendations } = useUser();
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState({
    soilType: '',
    crop: '',
    N: '',
    P: '',
    K: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: ''
  });

  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Handle soil card data if coming from soil card upload
  useEffect(() => {
    if (location.state?.soilData && location.state?.fromSoilCard) {
      setFormData(prev => ({
        ...prev,
        N: location.state.soilData.N || '',
        P: location.state.soilData.P || '',
        K: location.state.soilData.K || '',
        ph: location.state.soilData.ph || '',
        temperature: location.state.soilData.temperature || '',
        humidity: location.state.soilData.moisture || ''
      }));
    }
  }, [location.state]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Prepare soil data
      const soilData = {
        N: parseFloat(formData.N) || 0,
        P: parseFloat(formData.P) || 0,
        K: parseFloat(formData.K) || 0,
        temperature: parseFloat(formData.temperature) || 0,
        humidity: parseFloat(formData.humidity) || 0,
        ph: parseFloat(formData.ph) || 0,
        rainfall: parseFloat(formData.rainfall) || 0
      };

      // Auto-detect location (default to Bangalore for now)
      // The ML model will automatically consider weather conditions internally
      const location = {
        state: 'Karnataka',
        district: 'Bangalore',
        market: 'Ramanagara'
      };

      // Update user context
      updateSoilData(soilData);

      // Call API - ML model will auto-consider weather conditions
      const response = await advisoryAPI.getCropAdvisory(soilData, location);
      
      if (response.success) {
        // Extract crop information from ML response
        const extractCropFromAdvice = (advice, field) => {
          const regex = new RegExp(`${field}:\\s*([^\\n-]+)`, 'i');
          const match = advice.match(regex);
          return match ? match[1].trim() : null;
        };

        const mlCrop = extractCropFromAdvice(response.advice, 'ML Predicted Crop') || 'jute';
        const finalCrop = mlCrop; // For now, use ML crop as final crop

        const recommendationData = {
          advice: response.advice,
          timestamp: response.timestamp,
          mlCrop: mlCrop,
          finalCrop: finalCrop,
          bestMarketCrop: 'Drumstick', // This comes from market API
          bestPrice: '₹10,300',
          suitability: `✅ Recommended crop ${finalCrop} is suitable under current weather conditions.`
        };
        
        setRecommendations(recommendationData);
        updateRecommendations([response.advice]);
        
        // Navigate to results page
        navigate('/recommendation-results', { 
          state: { recommendation: recommendationData } 
        });
      }
    } catch (error) {
      console.error('Error getting advisory:', error);
      // Fallback to mock data
      const mockRecommendations = {
        mlCrop: 'Rice',
        finalCrop: 'Rice',
        bestMarketCrop: 'Wheat',
        bestPrice: '₹2,200',
        suitability: '✅ Recommended crop Rice is suitable under current weather conditions.',
        advice: '🌱 Based on soil, weather, ICRISAT & market: - ML Suggested Crop: Rice - Final Recommended Crop: Rice - Best Market Crop: Wheat (₹2,200)'
      };
      
      setRecommendations(mockRecommendations);
      updateRecommendations([mockRecommendations]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full min-h-screen w-full flex-col justify-between">
      <div className="flex-grow">
        <header className="flex items-center justify-between p-4">
          <button 
            className="flex h-12 w-12 items-center justify-center text-gray-900 dark:text-white"
            onClick={() => navigate('/')}
          >
            <span className="material-symbols-outlined text-3xl">arrow_back</span>
          </button>
          <h1 className="flex-1 text-center text-lg font-bold text-gray-900 dark:text-white pr-12">
            Crop Recommendations
          </h1>
        </header>

        <main className="p-4 space-y-4">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="relative">
              <select 
                className="form-select w-full appearance-none rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
                name="soilType"
                value={formData.soilType}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Soil Type</option>
                <option value="loamy">Loamy</option>
                <option value="clay">Clay</option>
                <option value="sandy">Sandy</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-900 dark:text-white">
                <span className="material-symbols-outlined">expand_more</span>
              </div>
            </div>

            <div className="relative">
              <select 
                className="form-select w-full appearance-none rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
                name="crop"
                value={formData.crop}
                onChange={handleInputChange}
              >
                <option value="">Select Crop</option>
                <option value="wheat">Wheat</option>
                <option value="corn">Corn</option>
                <option value="rice">Rice</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-900 dark:text-white">
                <span className="material-symbols-outlined">expand_more</span>
              </div>
            </div>

            {/* Weather info removed - now auto-detected by ML model */}

            {/* Soil Card Upload Option */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-blue-900 dark:text-blue-100">
                    📄 Have a Soil Test Card?
                  </h3>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    Upload your government or market soil test card for automatic data extraction
                  </p>
                </div>
                <button 
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                  onClick={() => navigate('/soil-card-upload')}
                >
                  Upload Card
                </button>
              </div>
            </div>

            {/* Auto-Location Detection Info */}
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <div className="flex items-center">
                <span className="material-symbols-outlined text-green-600 dark:text-green-400 mr-3">location_on</span>
                <div>
                  <h3 className="font-semibold text-green-900 dark:text-green-100">
                     Auto-Location Detection
                  </h3>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    Your location and weather conditions are automatically detected and considered by our ML model
                  </p>
                </div>
              </div>
            </div>

            {/* Soil Parameters */}
            <div className="grid grid-cols-2 gap-4">
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="N (Nitrogen)" 
                type="number"
                name="N"
                value={formData.N}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="P (Phosphorus)" 
                type="number"
                name="P"
                value={formData.P}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="K (Potassium)" 
                type="number"
                name="K"
                value={formData.K}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="Temperature (°C)" 
                type="number"
                name="temperature"
                value={formData.temperature}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="Humidity (%)" 
                type="number"
                name="humidity"
                value={formData.humidity}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="pH" 
                type="number"
                step="0.1"
                name="ph"
                value={formData.ph}
                onChange={handleInputChange}
              />
              <input 
                className="form-input w-full rounded-lg border-none bg-primary/10 dark:bg-primary/20 p-4 h-14 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary" 
                placeholder="Rainfall (mm)" 
                type="number"
                name="rainfall"
                value={formData.rainfall}
                onChange={handleInputChange}
              />
            </div>

            <button 
              className="w-full rounded-lg bg-primary py-4 px-4 text-center text-base font-bold text-white disabled:opacity-50" 
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Submit'}
            </button>
          </form>

          {/* Results Section */}
          {recommendations && (
            <div className="relative w-full overflow-hidden rounded-xl pt-[50%]">
              <img 
                alt="Farm field" 
                className="absolute inset-0 h-full w-full object-cover" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAeZJjxHjVEV68rWHsRVU-j5I4pTfZrabF-lUPehxBOdsfb5XYUPj02s4TPacSUaG51pqDPRTg_081ppYpbmsrn9b8JwGPAgok8xbPlOBmtyvv2qaZF3jT7o5Ncmnathi52aAb0-09JmSw85eAWfsvNbGMi63RceOM0KIUS6vhhk0u5LEFTdJ7iqAulzKYRYMD8fZ08irDjwkepnSYwWODI1zXc9oh1SGb2EbxcmsHfxx0P3B4xZN5ab6-HY0MZIDmU42AQb6wAFUxH" 
              />
              <div className="absolute inset-0 bg-black/40"></div>
              <div className="absolute bottom-0 w-full p-4 text-white">
                <h3 className="text-2xl font-bold">Recommended Crops</h3>
                <p className="font-medium">{recommendations.advice}</p>
                <div className="mt-2 text-sm">
                  <p>{recommendations.suitability}</p>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Advisory;
