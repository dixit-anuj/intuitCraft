import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header" role="banner">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo" aria-hidden="true">QB</div>
          <div className="title-section">
            <h1>QuickBooks Commerce</h1>
            <p>Sales Forecasting Dashboard</p>
          </div>
        </div>
        <div className="header-info">
          <span className="status-badge" role="status" aria-label="System status: live">
            <span className="status-dot" aria-hidden="true"></span>
            Live
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
