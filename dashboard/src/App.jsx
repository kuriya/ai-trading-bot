import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import './index.css';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPrediction = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/predict/BTCUSDT');
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to connect to AI server. The Python model is likely still training on 5-years of data in the background! Please wait a minute and it will auto-connect.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
    const interval = setInterval(fetchPrediction, 10000); // Retry/Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="dashboard-container">
        <div className="header">
          <h1>AI Trading Terminal</h1>
        </div>
        <div className="glass-card">
          <div className="loading">
            <Activity size={48} className="mx-auto mb-4" />
            <p>Initializing AI Models and crunching 5 years of historical data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="dashboard-container">
         <div className="header">
          <h1>AI Trading Terminal</h1>
        </div>
        <div className="glass-card state-neutral" style={{textAlign: 'center'}}>
           <Activity size={48} className="mx-auto mb-4" style={{color: 'var(--text-muted)'}} />
          <h2 style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>AI Model is Booting Up</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Determine state styling
  const isGood = data.forecast === 'GOOD TRADE';
  const isBad = data.forecast === 'BAD TRADE';
  
  let cardClass = 'glass-card state-neutral';
  let badgeClass = 'badge badge-neutral';
  let fillClass = 'confidence-fill fill-neutral';
  let Icon = Minus;

  if (isGood) {
    cardClass = 'glass-card state-good';
    badgeClass = 'badge badge-good';
    fillClass = 'confidence-fill fill-good';
    Icon = TrendingUp;
  } else if (isBad) {
    cardClass = 'glass-card state-bad';
    badgeClass = 'badge badge-bad';
    fillClass = 'confidence-fill fill-bad';
    Icon = TrendingDown;
  }

  return (
    <div className="dashboard-container">
      <div className="header">
        <h1>AI Trading Terminal</h1>
        <p>Institutional-grade predictive analytics</p>
      </div>

      <div className={cardClass}>
        <div className="prediction-header">
          <div className="coin-title">
            <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.svg" alt="BTC" width="48" height="48" />
            {data.coin}
          </div>
          <div className={badgeClass}>
            <Icon size={20} />
            {data.forecast}
          </div>
        </div>

        <div className="price-grid">
          <div className="price-box">
            <div className="price-label">Current Price</div>
            <div className="price-value">${data.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
          <div className="price-box">
            <div className="price-label">Take Profit (+5%)</div>
            <div className="price-value value-green">${data.target_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
          <div className="price-box">
            <div className="price-label">Stop Loss (-3%)</div>
            <div className="price-value value-red">${data.stop_loss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
        </div>

        <div>
          <div className="price-label">AI Neural Confidence Score</div>
          <div className="confidence-bar">
            <div className={fillClass} style={{ width: `${Math.max(data.confidence, 5)}%` }}></div>
          </div>
          <div className="confidence-text">
            <span>{data.confidence.toFixed(2)}% Certainty</span>
            <span style={{ color: 'var(--text-muted)' }}>48-Hour Forecast</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
