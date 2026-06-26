import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { API_BASE_URL } from '../services/api';


const Chat = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load supported languages
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat/languages`);
        const data = await response.json();
        if (data.success) {
          setSupportedLanguages(data.languages);
        }
      } catch (error) {
        console.error('Error loading languages:', error);
      }
    };

    loadLanguages();
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessages = {
      english: "Hello! I'm your agricultural assistant. I can help you with crop recommendations, pest control, fertilizers, market prices, and government schemes. How can I help you today?",
      hindi: "नमस्ते! मैं आपका कृषि सहायक हूं। मैं फसल की सिफारिशों, कीट नियंत्रण, उर्वरकों, बाजार की कीमतों और सरकारी योजनाओं में आपकी मदद कर सकता हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
      tamil: "வணக்கம்! நான் உங்கள் வேளாண் உதவியாளர். பயிர் பரிந்துரைகள், பூச்சி கட்டுப்பாடு, உரங்கள், சந்தை விலைகள் மற்றும் அரசாங்க திட்டங்களில் உங்களுக்கு உதவ முடியும். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?",
      kannada: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ಬೆಳೆ ಶಿಫಾರಸುಗಳು, ಕೀಟ ನಿಯಂತ್ರಣ, ಗೊಬ್ಬರಗಳು, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳಲ್ಲಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
    };

    if (messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: welcomeMessages[selectedLanguage] || welcomeMessages.english,
        timestamp: new Date().toISOString()
      }]);
    }
  }, [selectedLanguage]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Prepare context with user's soil and weather data
      const context = {};
      if (user.soilData) {
        context.soil_data = user.soilData;
      }
      if (user.weatherData) {
        context.weather_data = user.weatherData;
      }
      context.location = { district: 'Bangalore', state: 'Karnataka' };

      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          language: selectedLanguage,
          context: context
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          role: 'assistant',
          content: data.response || 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I could not connect to the server. Please check your internet connection and try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
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

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark flex flex-col">
      {/* Header */}
      <header className="sticky top-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between p-4">
          <button 
            className="flex h-12 w-12 items-center justify-center text-gray-900 dark:text-white"
            onClick={() => navigate('/')}
          >
            <span className="material-symbols-outlined text-3xl">arrow_back</span>
          </button>
          <div className="flex-1 text-center">
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">🤖 Farm Assistant</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">AI-Powered Agricultural Helper</p>
          </div>
          
          {/* Language Selector */}
          <div className="relative">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="appearance-none bg-primary/10 dark:bg-primary/20 text-gray-900 dark:text-white rounded-lg px-3 py-2 pr-8 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {supportedLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {getLanguageFlag(lang.code)} {lang.native}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
              <span className="material-symbols-outlined text-sm">expand_more</span>
            </div>
          </div>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary text-white'
                  : message.isError
                  ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 border border-red-300 dark:border-red-700'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-2 opacity-70 ${
                message.role === 'user' ? 'text-white' : 'text-gray-500 dark:text-gray-400'
              }`}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="animate-pulse flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="sticky bottom-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={selectedLanguage === 'hindi' ? 'अपना सवाल यहाँ लिखें...' : 
                         selectedLanguage === 'tamil' ? 'உங்கள் கேள்வியை இங்கே எழுதுங்கள்...' :
                         selectedLanguage === 'kannada' ? 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಬರೆಯಿರಿ...' :
                         'Ask your farming question here...'}
              className="w-full resize-none rounded-2xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              rows="1"
              style={{ minHeight: '44px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-primary hover:bg-primary/90 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded-2xl p-3 transition-colors duration-200 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
        
        {/* Quick Action Buttons */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[
            { text: selectedLanguage === 'hindi' ? 'फसल की सिफारिश' : 'Crop Recommendation', icon: '🌾' },
            { text: selectedLanguage === 'hindi' ? 'कीट नियंत्रण' : 'Pest Control', icon: '🐛' },
            { text: selectedLanguage === 'hindi' ? 'मौसम की जानकारी' : 'Weather Info', icon: '🌤️' },
            { text: selectedLanguage === 'hindi' ? 'बाजार की कीमत' : 'Market Price', icon: '💰' }
          ].map((action, index) => (
            <button
              key={index}
              onClick={() => setInputMessage(action.text)}
              className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-full text-sm font-medium transition-colors duration-200"
            >
              {action.icon} {action.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Chat;
