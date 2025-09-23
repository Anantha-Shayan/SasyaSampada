import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';

const Market = () => {
  const { updateMarketPrices } = useUser();
  const [searchTerm, setSearchTerm] = useState('');
  const [marketPrices, setMarketPrices] = useState([
    {
      id: 1,
      crop: 'Wheat',
      price: '₹2,200',
      unit: 'quintal',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC5aOalwWn9R5_JddUKFT1-8OG6PIeqSu-QndGvA-Ts5kMX9LA5TcoLZZv-KCRL50q9hqdvzAFrqp05eO1OwvMmsyMbMvyiNpcmXINEJWF8toaDKjLuAfcBW5pgl5fCB6bavT4C5g1QGOMpqO0gxyu5-C1PZaUYE6zx0uusCWsY3hPtyy78U48hDydGUY2nkbLu6mg6IFkf0pPH4VGlAjmLM-Qx0VC0HPoif0k02pSvcjsMy4bHwNZYu5cZ7T5LRZ0isW70cM1gOsp3',
      trend: 'up'
    },
    {
      id: 2,
      crop: 'Rice',
      price: '₹1,800',
      unit: 'quintal',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCvC1l5bY-BwvPBf_heu8lqV83xajgiwwyKuW7jf6l35CP_Yk60R1Ho5DkwLCvmfWnBuUkHqNA-gNKqeYv2yeOY5Ym8Rp36OJh0zgV3R930ipHUhi4JTztD5_ViC1B0uIJi_js-v-4W23a2jeZUW28edGE-Gznnmnp32kt7VViHCY98QO1KnNZO8DvtcdPpGSgBnWDl2vFpLGxvn3VIqmqwXq57-5xTYly9rOLSbyXgY6TkJ2jKzQ_IabD2p96kwZzUeiA4Ib3JlV5B',
      trend: 'down'
    },
    {
      id: 3,
      crop: 'Corn',
      price: '₹1,500',
      unit: 'quintal',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAYhoeENQWXeWBMJu_Cz_7bKa2uoEXMLx4f7LQaQsEiiQ4e0QAGyUDuqtFLx8XG_9LbQ_ADWzMjPXeWug5KYNT5rrIV7DjYFFYgP8-0xw54YDeNdko1MdQID0yi-JMTXw3cRpazEzi9naP-_6l-c2W18NpxdGAEaTPxmIlPOPnQbD9ITE4zPB-QdrKqPi2C1k9KUNi1E-qFJHdGqvi0VOBW6yWBorU-rq2STJGS__1JdkKCRmSi6gJqXiSV_XW0PxZSYzy09v2pw2Jz',
      trend: 'stable'
    },
    {
      id: 4,
      crop: 'Soybean',
      price: '₹2,500',
      unit: 'quintal',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCT1Ce7XwDb1skbhnmPV4MYiA3Cprta7DopFc8iUECG4YVKd28YdJmTBLsOwmT9kwf07q6WmmxVxSWxQgGnngdkRVQjsjlCweBSOhvaOU8BMjVmoo0ttdX_gmQchBnBsqlTOLtnCKBjMaNp78PzyfM94doYp-keJ1RTo4e1PwMC6D1v_ub4fMt1aqDM4Af2Mo2hMkmLzFppGfA5dFapub168aob-uU295GitugRJlHlFS6hZDrRRvWyY4FjEH2-uzzueaXTfg-sZ9gT',
      trend: 'up'
    },
    {
      id: 5,
      crop: 'Cotton',
      price: '₹3,000',
      unit: 'quintal',
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC4XJIQtITu3UKIRmwxDX853LNY0dV5j--c7zaTH8R3EYZdTXBr0vwLn0231vmvptsNhpvDxvHMYmGDECNC5CRUWLFzrFbOfVaH9tkMwvBRpx6DAp1aBsjE_6G_DxWsibX37rmcB6GmZvcRNDWIez9byLZnlQO8av80gLE8T_MpvNdwK5iZ2_8aRr8nJeT1W84pYOin7v4yotvfVkj5FOxoYZTGZR8jBq9w2y9baRPNaLh_O1Y6OaU7pj4saTg6WVBp8nP5yTLZU2hu',
      trend: 'stable'
    }
  ]);

  const [filteredPrices, setFilteredPrices] = useState(marketPrices);

  useEffect(() => {
    updateMarketPrices(marketPrices);
  }, [marketPrices, updateMarketPrices]);

  useEffect(() => {
    const filtered = marketPrices.filter(item =>
      item.crop.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPrices(filtered);
  }, [searchTerm, marketPrices]);

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return { icon: 'trending_up', color: 'text-green-500' };
      case 'down':
        return { icon: 'trending_down', color: 'text-red-500' };
      default:
        return { icon: 'trending_flat', color: 'text-gray-500' };
    }
  };

  return (
    <div className="flex flex-col h-screen justify-between max-w-md mx-auto">
      <div className="flex-grow overflow-y-auto pb-24">
        <header className="sticky top-0 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-sm z-10">
          <div className="flex items-center p-4">
            <button className="p-2 -ml-2">
              <span className="material-symbols-outlined text-gray-800 dark:text-gray-200">arrow_back</span>
            </button>
            <h1 className="text-xl font-bold flex-1 text-center pr-8 text-gray-900 dark:text-white">Market Prices</h1>
          </div>
        </header>

        <main className="px-4">
          <div className="relative my-4">
            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">search</span>
            <input 
              className="w-full h-14 pl-12 pr-4 rounded-lg bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/50 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400" 
              placeholder="Search for a crop" 
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Today's Market Prices</h2>
          
          <div className="space-y-2">
            {filteredPrices.map((item) => {
              const trend = getTrendIcon(item.trend);
              return (
                <div key={item.id} className="flex items-center gap-4 bg-white dark:bg-gray-800/20 p-3 rounded-lg">
                  <img 
                    alt={item.crop} 
                    className="w-14 h-14 rounded-lg object-cover" 
                    src={item.image} 
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-gray-900 dark:text-white">{item.crop}</p>
                      <span className={`material-symbols-outlined text-sm ${trend.color}`}>
                        {trend.icon}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Rs. {item.price}/{item.unit}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-primary">{item.price}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{item.trend}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {filteredPrices.length === 0 && (
            <div className="text-center py-8">
              <span className="material-symbols-outlined text-6xl text-gray-400 mb-4">search_off</span>
              <p className="text-gray-500 dark:text-gray-400">No crops found matching your search</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Market;
