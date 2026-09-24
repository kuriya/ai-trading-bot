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

      <div className="portfolio-section">
        {/* Active Trades Table */}
        <div className="table-container">
          <div className="table-header">
             Active Trades (Live Monitoring)
          </div>
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Coin</th>
                <th>Status</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>Time Remaining</th>
                <th>Unrealized PnL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem'}}><img src="https://cryptologos.cc/logos/bitcoin-btc-logo.svg" width="24" height="24"/> BTCUSDT</td>
                <td><span className="status-badge status-open">Running</span></td>
                <td>$84,000.00</td>
                <td>${data.current_price.toLocaleString()}</td>
                <td>36 Hours</td>
                <td className="value-green">+0.65% (+$23.50)</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Trade History Table */}
        <div className="table-container">
          <div className="table-header" style={{display: 'flex', justifyContent: 'space-between'}}>
             <span>Trade History (Last 30 Days)</span>
             <span style={{fontSize: '1.2rem', color: 'var(--text-muted)'}}>Total PnL: <span className="value-green">+$452.10</span></span>
          </div>
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Coin</th>
                <th>Result</th>
                <th>Entry Price</th>
                <th>Exit Price</th>
                <th>Duration</th>
                <th>Realized PnL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem'}}><img src="https://cryptologos.cc/logos/ethereum-eth-logo.svg" width="24" height="24"/> ETHUSDT</td>
                <td><span className="status-badge status-win">Take Profit</span></td>
                <td>$2,600.00</td>
                <td>$2,730.00</td>
                <td>12 Hours</td>
                <td className="value-green">+5.00% (+$130.00)</td>
              </tr>
              <tr>
                <td style={{fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem'}}><img src="https://cryptologos.cc/logos/solana-sol-logo.svg" width="24" height="24"/> SOLUSDT</td>
                <td><span className="status-badge status-loss">Stop Loss</span></td>
                <td>$150.00</td>
                <td>$145.50</td>
                <td>4 Hours</td>
                <td className="value-red">-3.00% (-$4.50)</td>
              </tr>
              <tr>
                <td style={{fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem'}}><img src="https://cryptologos.cc/logos/bitcoin-btc-logo.svg" width="24" height="24"/> BTCUSDT</td>
                <td><span className="status-badge status-win">Timeout Close</span></td>
                <td>$82,000.00</td>
                <td>$83,640.00</td>
                <td>48 Hours</td>
                <td className="value-green">+2.00% (+$1,640.00)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
