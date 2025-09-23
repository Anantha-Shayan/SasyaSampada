import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { useLanguage } from '../context/LanguageContext';
import { weatherAPI } from '../services/api';
import ChatModal from '../components/ChatModal';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();
  const { updateWeatherData } = useUser();
  const { currentLanguage, supportedLanguages, changeLanguage, getLanguageFlag, t } = useLanguage();
  const [weather, setWeather] = useState({
    temp: 28,
    condition: 'Sunny',
    humidity: 65,
    rainfall: 0
  });
  const [isLoadingWeather, setIsLoadingWeather] = useState(false);
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);

  // Close language dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isLanguageDropdownOpen && !event.target.closest('.language-dropdown')) {
        setIsLanguageDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isLanguageDropdownOpen]);

  // Fetch real weather data
  const fetchWeatherData = async (city = 'Bangalore') => {
    setIsLoadingWeather(true);
    try {
      const response = await weatherAPI.getWeather(city);
      if (response.success && response.weather) {
        const weatherData = response.weather;
        const updatedWeather = {
          temp: Math.round(weatherData.temp || 28),
          condition: weatherData.condition || 'Sunny',
          humidity: weatherData.humidity || 65,
          rainfall: weatherData.rainfall || 0
        };
        setWeather(updatedWeather);
        updateWeatherData(updatedWeather);
      }
    } catch (error) {
      console.error('Failed to fetch weather data:', error);
      // Keep default weather data on error
    } finally {
      setIsLoadingWeather(false);
    }
  };

  useEffect(() => {
    // Fetch real weather data on component mount
    fetchWeatherData();
  }, []);

  // Get weather icon based on condition
  const getWeatherIcon = (condition, rainfall) => {
    if (rainfall > 5) return '🌧️';
    if (condition.toLowerCase().includes('sunny') || condition.toLowerCase().includes('hot')) return '☀️';
    if (condition.toLowerCase().includes('cloud') || condition.toLowerCase().includes('humid')) return '☁️';
    if (condition.toLowerCase().includes('cool') || condition.toLowerCase().includes('pleasant')) return '🌤️';
    return '☀️';
  };

  const quickAdvisoryItems = [
    {
      id: 1,
      title: 'Best Crops for Your Soil',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCLWr7PJORjb2G2ABf-Unarfkr9h_uJYulUzR2ViCTgwd-4m-f9W7Auj932SNAgd1tzFxb9Qrdf2HZzuzdbQypu-uHSqWkqzW8FDCMO9Lqh5yCDYe16_B-nRz8jBf7wKDnUeE2i5LjlZdAhyNdVMHa5YXXUob44OcYrcKI2kK8WWi6aRNiHQ4F4K1Ve1lkjdBOdnutXUvp4HCdRfFhDekdwJil5bEskejztXLyredgEIk5TLlOUZbw5HhsNrwlSkliKZ9L_K7-vwU1D',
      onClick: () => navigate('/advisory')
    },
    {
      id: 2,
      title: 'Optimize Fertilizer Usage',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCrbm4aiBrEJPEPoGdLsYd-H4fMoxcZKFVas0rtRMu5F2PsS3vP4E2ppp3G6zFHkNOemAUv-Jtw1zTExcYlYu1uRUA-XVb7ee64903RYE2broW6K0h3QVZHLzh-ogxal0me71HMRfjUQOmO4fSmgpmwvJXW1EwXA5BoqZ40Xd7Imf1JJ3FKVm8YhSsKfasqdeiEeFdQWvR9QgE9PpQCcrlJpoc5yTbsq0tEpYvnRz4Fpz8cX2hpNMIIWdbaqzwSvKHpcw3ihJtc9nTs',
      onClick: () => navigate('/advisory')
    },
    {
      id: 3,
      title: 'Pest Control Tips',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAQOVSZEd9lwWgwZvebzMlmKkOmt9iEhjygwr0KPKBofwuYSaEAZYYMa4mCWc7GjbMeH3WBS-MTrqML4FzQwEnInSNWtYkY8sBSE5C7LvrmDFKO7XS-GYv4vnoANDzRUhsXqc5YFBITyOxDMH-Z4Av8eZVqRuFOGcK4_3eTjwQGYLVRl6COQXDG3NqtUGiWkMaoHSMV8cw-VxUJTT5JyLJ_oCoMp2g4AfPLbC3JqnBQqmh-goepYIUanWNCLh5icsX9dwxSFDHENJv9',
      onClick: () => navigate('/pest')
    }
  ];

  const mandiPrices = [
    { crop: 'Wheat', price: '₹2,000/q' },
    { crop: 'Rice', price: '₹1,800/q' },
    { crop: 'Cotton', price: '₹5,500/q' },
    { crop: 'Soybean', price: '₹4,500/q' }
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <header className="sticky top-0 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-sm z-10">
        <div className="flex items-center justify-between p-4">
          <div className="w-10"></div>
          <h1 className="text-lg font-bold">{t('farmers_dashboard', "Farmer's Dashboard")}</h1>

          {/* Language Selector */}
          <div className="relative language-dropdown">
            <button
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
              onClick={() => setIsLanguageDropdownOpen(!isLanguageDropdownOpen)}
            >
              <svg className="text-stone-800 dark:text-stone-200" fill="currentColor" height="24" viewBox="0 0 256 256" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM101.63,168h52.74C149,186.34,140,202.87,128,215.89,116,202.87,107,186.34,101.63,168ZM98,152a145.72,145.72,0,0,1,0-48h60a145.72,145.72,0,0,1,0,48ZM40,128a87.61,87.61,0,0,1,3.33-24H81.79a161.79,161.79,0,0,0,0,48H43.33A87.61,87.61,0,0,1,40,128ZM154.37,88H101.63C107,69.66,116,53.13,128,40.11,140,53.13,149,69.66,154.37,88Zm19.84,16h38.46a88.15,88.15,0,0,1,0,48H174.21a161.79,161.79,0,0,0,0-48Zm32.16-16H170.94a142.39,142.39,0,0,0-20.26-45A88.37,88.37,0,0,1,206.37,88ZM105.32,43A142.39,142.39,0,0,0,85.06,88H49.63A88.37,88.37,0,0,1,105.32,43ZM49.63,168H85.06a142.39,142.39,0,0,0,20.26,45A88.37,88.37,0,0,1,49.63,168Zm101.05,45a142.39,142.39,0,0,0,20.26-45h35.43A88.37,88.37,0,0,1,150.68,213Z"></path>
              </svg>
            </button>

            {/* Language Dropdown */}
            {isLanguageDropdownOpen && (
              <div className="absolute right-0 top-full mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 min-w-[200px] z-20">
                <div className="p-2">
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 px-3 py-2 border-b border-gray-200 dark:border-gray-700">
                    Select Language
                  </div>
                  {supportedLanguages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        changeLanguage(lang.code);
                        setIsLanguageDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2 ${
                        currentLanguage === lang.code ? 'bg-primary/10 text-primary' : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <span>{getLanguageFlag(lang.code)}</span>
                      <span>{lang.native}</span>
                      {currentLanguage === lang.code && (
                        <span className="material-symbols-outlined text-sm ml-auto">check</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="px-4 pb-4 space-y-6">
        {/* Weather Section */}
        <section>
          <div className="flex items-center gap-4 p-4 rounded-lg bg-white dark:bg-black/20">
            <div className="text-4xl">
              {isLoadingWeather ? '🔄' : getWeatherIcon(weather.condition, weather.rainfall)}
            </div>
            <div>
              <p className="font-medium">{t('your_farm', 'Your Farm')}</p>
              {isLoadingWeather ? (
                <p className="text-stone-600 dark:text-stone-400">{t('loading_weather', 'Loading weather...')}</p>
              ) : (
                <p className="text-stone-600 dark:text-stone-400">{weather.condition}, {weather.temp}°C</p>
              )}
            </div>
          </div>
        </section>

        {/* Pest Alert Section */}
        <section>
          <div className="relative rounded-xl overflow-hidden text-white">
            <img 
              alt="Pest outbreak alert" 
              className="absolute inset-0 w-full h-full object-cover" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDLTviYh4KPUfirp_Wac7I3pn3Ymf64nUIm1nBQ49dpQMXSP5dqBaNPBXThPNk58Z8IxlSp5LtZXl2PiL-QCzc1aer3o0hUrw_bohL3_NvUpC9nOn83N4XbvadFZBHPvsjqyXwHRNMwchImscLl-hfMVhR_g032YD9LPcgM25RKTnvphg-Hd9iZvXUi47AAtN8sOWbVUrc_za3wm69prF0kuJ4lSW1h3_2SjaB3OwLpdStc5DvJkwsH-wiVQExE2DnYP6_jgi0fiUpL" 
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
            <div className="relative p-4 flex flex-col justify-end min-h-[160px]">
              <h3 className="text-xl font-bold">Pest Outbreak Detected</h3>
              <p className="text-sm">Take immediate action to protect your crops.</p>
            </div>
          </div>
        </section>

        {/* Quick Advisory Section */}
        <section>
          <h2 className="text-lg font-bold mb-2">Quick Advisory</h2>
          <div className="flex overflow-x-auto gap-4 no-scrollbar -mx-4 px-4">
            {quickAdvisoryItems.map((item) => (
              <div key={item.id} className="flex-shrink-0 w-40 space-y-2" onClick={item.onClick}>
                <img 
                  alt={item.title} 
                  className="w-full h-40 object-cover rounded-lg cursor-pointer" 
                  src={item.image} 
                />
                <p className="font-medium text-sm">{item.title}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Mandi Prices Section */}
        <section>
          <h2 className="text-lg font-bold mb-2">{t('mandi_prices', 'Mandi Prices')}</h2>
          <div className="overflow-hidden relative bg-white dark:bg-black/20 rounded-lg">
            <div className="flex animate-marquee whitespace-nowrap">
              {mandiPrices.map((item, index) => (
                <div key={index} className="mx-4 py-2">
                  {item.crop}: <span className="font-semibold text-primary">{item.price}</span>
                </div>
              ))}
            </div>
            <div className="flex animate-marquee2 whitespace-nowrap absolute top-0">
              {mandiPrices.map((item, index) => (
                <div key={index} className="mx-4 py-2">
                  {item.crop}: <span className="font-semibold text-primary">{item.price}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      {/* Chat Input */}
      <div className="sticky bottom-0 bg-background-light dark:bg-background-dark border-t border-stone-200 dark:border-stone-800">
        <div className="p-2 @container">
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => setIsChatModalOpen(true)}
          >
            <input
              className="flex-1 bg-white dark:bg-black/20 border-stone-300 dark:border-stone-700 rounded-full px-4 py-2.5 focus:ring-primary focus:border-primary pointer-events-none"
              placeholder={`🤖 ${t('chat_placeholder', 'Ask your farming assistant...')}`}
              type="text"
              readOnly
            />
            <button className="p-2.5 rounded-full hover:bg-stone-200 dark:hover:bg-stone-800 bg-primary/10">
              <span className="material-symbols-outlined text-primary">smart_toy</span>
            </button>
          </div>
          <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-1">
            💬 {t('multilingual_assistant', 'Multilingual AI Assistant')} • Hindi, Tamil, Kannada & more
          </p>
        </div>
      </div>

      {/* Chat Modal */}
      <ChatModal
        isOpen={isChatModalOpen}
        onClose={() => setIsChatModalOpen(false)}
      />
    </div>
  );
};

export default Home;
