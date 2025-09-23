import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('english');
  const [supportedLanguages, setSupportedLanguages] = useState([]);

  // Load supported languages from backend
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/chat/languages');
        const data = await response.json();
        if (data.success) {
          setSupportedLanguages(data.languages);
        }
      } catch (error) {
        console.error('Error loading languages:', error);
        // Fallback languages
        setSupportedLanguages([
          { code: 'english', name: 'English', native: 'English' },
          { code: 'hindi', name: 'Hindi', native: 'हिंदी' },
          { code: 'tamil', name: 'Tamil', native: 'தமிழ்' },
          { code: 'kannada', name: 'Kannada', native: 'ಕನ್ನಡ' }
        ]);
      }
    };

    loadLanguages();
  }, []);

  // Load saved language from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('agrigrow_language');
    if (savedLanguage) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const changeLanguage = (languageCode) => {
    setCurrentLanguage(languageCode);
    localStorage.setItem('agrigrow_language', languageCode);
  };

  const getLanguageFlag = (langCode) => {
    const flags = {
      english: '🇬🇧',
      hindi: '🇮🇳',
      tamil: '🇮🇳',
      kannada: '🇮🇳',
      telugu: '🇮🇳',
      marathi: '🇮🇳',
      gujarati: '🇮🇳',
      punjabi: '🇮🇳'
    };
    return flags[langCode] || '🌐';
  };

  // Translation function (basic implementation)
  const t = (key, fallback) => {
    const translations = {
      english: {
        'home': 'Home',
        'advisory': 'Advisory',
        'pest': 'Pest',
        'weather': 'Weather',
        'market': 'Market',
        'chat_placeholder': 'Ask your farming assistant...',
        'multilingual_assistant': 'Multilingual AI Assistant',
        'farmers_dashboard': "Farmer's Dashboard",
        'your_farm': 'Your Farm',
        'loading_weather': 'Loading weather...',
        'mandi_prices': 'Mandi Prices',
        'ask_question': 'Ask a question...',
        'crop_recommendation': 'Crop Recommendation',
        'pest_control': 'Pest Control',
        'weather_info': 'Weather Info',
        'market_price': 'Market Price'
      },
      hindi: {
        'home': 'होम',
        'advisory': 'सलाह',
        'pest': 'कीट',
        'weather': 'मौसम',
        'market': 'बाजार',
        'chat_placeholder': 'अपने कृषि सहायक से पूछें...',
        'multilingual_assistant': 'बहुभाषी AI सहायक',
        'farmers_dashboard': 'किसान डैशबोर्ड',
        'your_farm': 'आपका खेत',
        'loading_weather': 'मौसम लोड हो रहा है...',
        'mandi_prices': 'मंडी भाव',
        'ask_question': 'सवाल पूछें...',
        'crop_recommendation': 'फसल की सिफारिश',
        'pest_control': 'कीट नियंत्रण',
        'weather_info': 'मौसम की जानकारी',
        'market_price': 'बाजार की कीमत'
      },
      tamil: {
        'home': 'முகப்பு',
        'advisory': 'ஆலோசனை',
        'pest': 'பூச்சி',
        'weather': 'வானிலை',
        'market': 'சந்தை',
        'chat_placeholder': 'உங்கள் வேளாண் உதவியாளரிடம் கேளுங்கள்...',
        'multilingual_assistant': 'பல்மொழி AI உதவியாளர்',
        'farmers_dashboard': 'விவசாயி டாஷ்போர்டு',
        'your_farm': 'உங்கள் பண்ணை',
        'loading_weather': 'வானிலை ஏற்றுகிறது...',
        'mandi_prices': 'மண்டி விலைகள்',
        'ask_question': 'கேள்வி கேளுங்கள்...',
        'crop_recommendation': 'பயிர் பரிந்துரை',
        'pest_control': 'பூச்சி கட்டுப்பாடு',
        'weather_info': 'வானிலை தகவல்',
        'market_price': 'சந்தை விலை'
      },
      kannada: {
        'home': 'ಮುಖ್ಯ',
        'advisory': 'ಸಲಹೆ',
        'pest': 'ಕೀಟ',
        'weather': 'ಹವಾಮಾನ',
        'market': 'ಮಾರುಕಟ್ಟೆ',
        'chat_placeholder': 'ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕರನ್ನು ಕೇಳಿ...',
        'multilingual_assistant': 'ಬಹುಭಾಷಾ AI ಸಹಾಯಕ',
        'farmers_dashboard': 'ರೈತ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'your_farm': 'ನಿಮ್ಮ ಫಾರ್ಮ್',
        'loading_weather': 'ಹವಾಮಾನ ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
        'mandi_prices': 'ಮಂಡಿ ಬೆಲೆಗಳು',
        'ask_question': 'ಪ್ರಶ್ನೆ ಕೇಳಿ...',
        'crop_recommendation': 'ಬೆಳೆ ಶಿಫಾರಸು',
        'pest_control': 'ಕೀಟ ನಿಯಂತ್ರಣ',
        'weather_info': 'ಹವಾಮಾನ ಮಾಹಿತಿ',
        'market_price': 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ'
      }
    };

    return translations[currentLanguage]?.[key] || fallback || key;
  };

  const value = {
    currentLanguage,
    supportedLanguages,
    changeLanguage,
    getLanguageFlag,
    t
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
