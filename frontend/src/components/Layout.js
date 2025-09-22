import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navigation from './Navigation';

const Layout = () => {
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen bg-background-light dark:bg-background-dark">
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
      <Navigation currentPath={location.pathname} />
    </div>
  );
};

export default Layout;
