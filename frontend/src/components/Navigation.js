import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = ({ currentPath }) => {
  const navItems = [
    { path: '/', icon: 'home', label: 'Home' },
    { path: '/advisory', icon: 'agriculture', label: 'Advisory' },
    { path: '/pest', icon: 'bug_report', label: 'Pest' },
    { path: '/weather', icon: 'wb_sunny', label: 'Weather' },
    { path: '/market', icon: 'storefront', label: 'Market' }
  ];

  return (
    <footer className="sticky bottom-0 bg-background-light dark:bg-background-dark border-t border-stone-200 dark:border-stone-800">
      <nav className="flex justify-around py-1">
        {navItems.map((item) => {
          const isActive = currentPath === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center gap-1 p-2 rounded-lg w-1/5 ${
                isActive 
                  ? 'text-primary' 
                  : 'text-stone-500 dark:text-stone-400 hover:text-primary dark:hover:text-primary'
              }`}
            >
              <span className="material-symbols-outlined text-2xl">
                {item.icon}
              </span>
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </footer>
  );
};

export default Navigation;
