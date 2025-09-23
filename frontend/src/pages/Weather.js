import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { weatherAPI } from '../services/api';

const Weather = () => {
  const { updateWeatherData } = useUser();
  const [location, setLocation] = useState('');
  const [weather, setWeather] = useState({
    temp: 28,
    condition: 'Partly cloudy',
    humidity: 65,
    windSpeed: 12,
    pressure: 980,
    rainChance: 20,
    rainfall: 0
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Generate dynamic forecast based on current weather
  const generateForecast = (currentWeather) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const icons = ['sunny', 'cloud', 'rainy', 'partly_cloudy_day'];

    return days.map((day, index) => {
      const tempVariation = Math.random() * 6 - 3; // ±3°C variation
      const baseTemp = currentWeather.temp + tempVariation;
      const rainChance = currentWeather.rainfall > 0 ?
        Math.max(20, currentWeather.rainfall * 10 + Math.random() * 20) :
        Math.random() * 30;

      let icon = 'sunny';
      if (rainChance > 50) icon = 'rainy';
      else if (rainChance > 25) icon = 'cloud';
      else if (index % 2 === 0) icon = 'partly_cloudy_day';

      return {
        day,
        icon,
        temp: Math.round(baseTemp),
        rainChance: Math.round(rainChance)
      };
    });
  };

  const [forecast, setForecast] = useState(generateForecast(weather));

  // Generate dynamic alerts based on weather conditions
  const generateAlerts = (weatherData) => {
    const alerts = [];

    // Frost alert for low temperatures
    if (weatherData.temp < 5) {
      alerts.push({
        id: 1,
        type: 'warning',
        icon: 'ac_unit',
        title: 'Frost Alert',
        message: 'Very low temperature detected. Protect sensitive crops immediately.',
        color: 'yellow'
      });
    }

    // Heat stress alert for high temperatures
    if (weatherData.temp > 35) {
      alerts.push({
        id: 2,
        type: 'danger',
        icon: 'thermostat',
        title: 'Heat Stress',
        message: 'High temperature detected. Ensure adequate irrigation and shade.',
        color: 'red'
      });
    }

    // High humidity alert
    if (weatherData.humidity > 80) {
      alerts.push({
        id: 3,
        type: 'warning',
        icon: 'humidity_percentage',
        title: 'High Humidity',
        message: 'High humidity may promote fungal diseases. Monitor crops closely.',
        color: 'yellow'
      });
    }

    // Rainfall alert
    if (weatherData.rainfall > 10) {
      alerts.push({
        id: 4,
        type: 'info',
        icon: 'water_drop',
        title: 'Heavy Rainfall',
        message: 'Significant rainfall detected. Check drainage and avoid field operations.',
        color: 'blue'
      });
    }

    // Optimal spraying conditions
    if (weatherData.temp >= 20 && weatherData.temp <= 30 &&
        weatherData.humidity < 70 && weatherData.rainfall === 0) {
      alerts.push({
        id: 5,
        type: 'info',
        icon: 'spray',
        title: 'Optimal Spraying',
        message: 'Good conditions for pesticide/fertilizer application.',
        color: 'blue'
      });
    }

    return alerts;
  };

  const [alerts, setAlerts] = useState(generateAlerts(weather));

  // Fetch weather data from API
  const fetchWeatherData = async (city) => {
    if (!city.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      console.log('Fetching weather for:', city);
      const response = await weatherAPI.getWeather(city);

      if (response.success && response.weather) {
        const weatherData = response.weather;

        // Map API response to our weather state structure
        const updatedWeather = {
          temp: Math.round(weatherData.temp || 28),
          humidity: weatherData.humidity || 65,
          rainfall: weatherData.rainfall || 0,
          condition: weatherData.condition || getWeatherCondition(weatherData.temp, weatherData.humidity, weatherData.rainfall),
          windSpeed: 12, // Default as API doesn't provide this
          pressure: 980, // Default as API doesn't provide this
          rainChance: weatherData.rainfall > 0 ? Math.min(90, weatherData.rainfall * 10) : 20
        };

        setWeather(updatedWeather);
        setForecast(generateForecast(updatedWeather));
        setAlerts(generateAlerts(updatedWeather));
        updateWeatherData(updatedWeather);

        console.log('Weather updated successfully:', updatedWeather);
      } else {
        throw new Error('Invalid weather data received');
      }
    } catch (error) {
      console.error('Error fetching weather:', error);
      setError(error.message);

      // Use fallback weather data
      const fallbackWeather = {
        temp: 28,
        condition: 'Partly cloudy',
        humidity: 65,
        windSpeed: 12,
        pressure: 980,
        rainChance: 20,
        rainfall: 0
      };
      setWeather(fallbackWeather);
      setForecast(generateForecast(fallbackWeather));
      setAlerts(generateAlerts(fallbackWeather));
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to determine weather condition based on data
  const getWeatherCondition = (temp, humidity, rainfall) => {
    if (rainfall > 5) return 'Rainy';
    if (humidity > 80) return 'Cloudy';
    if (temp > 30) return 'Hot and sunny';
    if (temp < 15) return 'Cool';
    return 'Partly cloudy';
  };

  // Auto-detect location and fetch weather
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // For now, use default location - in production, you'd use reverse geocoding
          const defaultLocation = 'Bangalore';
          setLocation(defaultLocation);
          fetchWeatherData(defaultLocation);
        },
        (error) => {
          console.log('Location access denied:', error);
          const defaultLocation = 'Bangalore';
          setLocation(defaultLocation);
          fetchWeatherData(defaultLocation);
        }
      );
    } else {
      const defaultLocation = 'Bangalore';
      setLocation(defaultLocation);
      fetchWeatherData(defaultLocation);
    }
  }, []);

  // Handle location search
  const handleLocationSearch = (e) => {
    if (e.key === 'Enter' || e.type === 'click') {
      const city = location.split(',')[0].trim(); // Extract city name
      fetchWeatherData(city);
    }
  };

  const getIconColor = (icon) => {
    switch (icon) {
      case 'sunny': return 'text-yellow-500';
      case 'cloud': return 'text-gray-400';
      case 'rainy': return 'text-blue-400';
      case 'partly_cloudy_day': return 'text-gray-500';
      default: return 'text-gray-400';
    }
  };

  const getAlertColors = (color) => {
    switch (color) {
      case 'yellow':
        return 'bg-yellow-100/50 dark:bg-yellow-900/20 border-yellow-400/50 dark:border-yellow-500/30 text-yellow-600 dark:text-yellow-400 text-yellow-800 dark:text-yellow-300 text-yellow-700 dark:text-yellow-400';
      case 'red':
        return 'bg-red-100/50 dark:bg-red-900/20 border-red-400/50 dark:border-red-500/30 text-red-600 dark:text-red-400 text-red-800 dark:text-red-300 text-red-700 dark:text-red-400';
      case 'blue':
        return 'bg-blue-100/50 dark:bg-blue-900/20 border-blue-400/50 dark:border-blue-500/30 text-blue-600 dark:text-blue-400 text-blue-800 dark:text-blue-300 text-blue-700 dark:text-blue-400';
      default:
        return 'bg-gray-100/50 dark:bg-gray-900/20 border-gray-400/50 dark:border-gray-500/30 text-gray-600 dark:text-gray-400 text-gray-800 dark:text-gray-300 text-gray-700 dark:text-gray-400';
    }
  };

  // Get weather icon based on condition
  const getWeatherIcon = (condition, rainfall) => {
    if (rainfall > 5) return 'rainy';
    if (condition.toLowerCase().includes('sunny') || condition.toLowerCase().includes('hot')) return 'sunny';
    if (condition.toLowerCase().includes('cloud')) return 'cloud';
    if (condition.toLowerCase().includes('cool')) return 'partly_cloudy_day';
    return 'partly_cloudy_day';
  };

  return (
    <div className="flex flex-col min-h-screen justify-between">
      <main className="flex-grow">
        <header className="flex items-center p-4">
          <button className="p-2">
            <span className="material-symbols-outlined text-gray-800 dark:text-gray-200">arrow_back</span>
          </button>
          <h1 className="flex-1 text-center font-bold text-lg text-gray-900 dark:text-white pr-10">Weather</h1>
        </header>

        <div className="px-4 pb-4">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">search</span>
            <input
              className="w-full bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 rounded-lg py-3 pl-10 pr-12 focus:outline-none focus:ring-2 focus:ring-primary/50 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              placeholder="Search for a location (e.g., Mumbai, Delhi)"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const city = location.split(',')[0].trim();
                  fetchWeatherData(city);
                }
              }}
            />
            <button
              onClick={() => {
                const city = location.split(',')[0].trim();
                fetchWeatherData(city);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-primary hover:text-primary/80"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="material-symbols-outlined animate-spin">refresh</span>
              ) : (
                <span className="material-symbols-outlined">search</span>
              )}
            </button>
          </div>
          {location && (
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 flex items-center">
              <span className="material-symbols-outlined text-sm mr-1">location_on</span>
              Current location: {location}
            </div>
          )}
          {error && (
            <div className="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center">
              <span className="material-symbols-outlined text-sm mr-1">error</span>
              {error}
            </div>
          )}
        </div>

        {/* Today's Weather */}
        <section className="p-4">
          <div className="bg-white dark:bg-zinc-800/20 rounded-xl shadow-sm overflow-hidden">
            {isLoading ? (
              <div className="p-8 text-center">
                <span className="material-symbols-outlined text-4xl text-primary animate-spin">refresh</span>
                <p className="mt-2 text-gray-600 dark:text-gray-400">Loading weather data...</p>
              </div>
            ) : (
              <div className="p-4">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Today's Snapshot</h2>
                <div className="flex items-center mt-2">
                  <span className="material-symbols-outlined text-6xl text-primary">
                    {getWeatherIcon(weather.condition, weather.rainfall)}
                  </span>
                  <div className="ml-4">
                    <p className="text-4xl font-bold text-gray-900 dark:text-white">{weather.temp}°C</p>
                    <p className="text-gray-600 dark:text-gray-400">{weather.condition}</p>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-primary mr-2">water_drop</span>
                    <span className="text-gray-700 dark:text-gray-300">{weather.rainChance}% rain</span>
                  </div>
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-primary mr-2">air</span>
                    <span className="text-gray-700 dark:text-gray-300">{weather.windSpeed} km/h</span>
                  </div>
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-primary mr-2">compress</span>
                    <span className="text-gray-700 dark:text-gray-300">{weather.pressure} hPa</span>
                  </div>
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-primary mr-2">humidity_percentage</span>
                    <span className="text-gray-700 dark:text-gray-300">{weather.humidity}% humidity</span>
                  </div>
                  {weather.rainfall > 0 && (
                    <div className="flex items-center col-span-2">
                      <span className="material-symbols-outlined text-primary mr-2">rainy</span>
                      <span className="text-gray-700 dark:text-gray-300">Rainfall: {weather.rainfall}mm</span>
                    </div>
                  )}
                </div>
                <div className="mt-4 bg-primary/10 dark:bg-primary/20 p-3 rounded-lg flex items-start">
                  <span className="material-symbols-outlined text-primary mr-2 text-xl">lightbulb</span>
                  <p className="text-sm text-primary font-medium flex-1">
                    {weather.rainfall > 0
                      ? "Rainfall detected. Avoid field operations and check drainage systems."
                      : weather.temp > 30
                        ? "High temperature. Ensure adequate irrigation for your crops."
                        : "Good weather conditions for farming activities."
                    }
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* 5-Day Forecast */}
        <section className="py-4">
          <h2 className="text-lg font-bold px-4 mb-2 text-gray-900 dark:text-white">Next 5 Days</h2>
          <div className="flex overflow-x-auto space-x-3 px-4 pb-4 [-ms-scrollbar-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {forecast.map((day, index) => (
              <div key={index} className="flex-shrink-0 w-28 text-center bg-white dark:bg-zinc-800/20 rounded-xl p-3 shadow-sm">
                <p className="font-medium text-gray-800 dark:text-gray-200">{day.day}</p>
                <span className={`material-symbols-outlined text-4xl my-2 ${getIconColor(day.icon)}`}>
                  {day.icon}
                </span>
                <p className="font-bold text-gray-900 dark:text-white">{day.temp}°C</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{day.rainChance}% rain</p>
              </div>
            ))}
          </div>
        </section>

        {/* Risk Alerts */}
        <section className="p-4 space-y-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Risk Alerts</h2>
          {alerts.length > 0 ? (
            alerts.map((alert) => {
              const colors = getAlertColors(alert.color);
              const colorClasses = colors.split(' ');
              return (
                <div key={alert.id} className={`${colorClasses[0]} ${colorClasses[1]} rounded-xl p-4 flex items-center`}>
                  <span className={`material-symbols-outlined ${colorClasses[2]} text-3xl mr-4`}>
                    {alert.icon}
                  </span>
                  <div>
                    <h3 className={`font-bold ${colorClasses[3]}`}>{alert.title}</h3>
                    <p className={`text-sm ${colorClasses[4]}`}>{alert.message}</p>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="bg-green-100/50 dark:bg-green-900/20 border border-green-400/50 dark:border-green-500/30 rounded-xl p-4 flex items-center">
              <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-3xl mr-4">check_circle</span>
              <div>
                <h3 className="font-bold text-green-800 dark:text-green-300">All Clear</h3>
                <p className="text-sm text-green-700 dark:text-green-400">No weather-related risks detected for your crops.</p>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default Weather;
