import React, { useState, useEffect } from 'react';
import TimeInput from './components/TimeInput';

import './App.css';

const App = () => {
  const storedDate = localStorage.getItem('date');
  const currentDate = new Date().toISOString().split('T')[0];

  const [chartData, setChartData] = useState([]);
  const [timeEntered, setTimeEntered] = useState(storedDate === currentDate && localStorage.getItem('timeEntered') === 'true');
  const [userTime, setUserTime] = useState(localStorage.getItem('userTime'));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (timeEntered) {
      // Create AbortController to cancel fetch on unmount
      const abortController = new AbortController();

      setIsLoading(true);
      fetch('/api/chartData', { signal: abortController.signal })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          setChartData(data.data);
          setIsLoading(false);
        })
        .catch(error => {
          // Ignore abort errors (expected on unmount)
          if (error.name === 'AbortError') {
            return;
          }
          console.error('Error fetching chart data:', error);
          setError('Failed to load chart data. Please try again later.');
          setIsLoading(false);
        });

      // Cleanup function to abort fetch if component unmounts
      return () => {
        abortController.abort();
      };
    }
  }, [timeEntered]);

  const handleTimeInput = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = String(time % 60).padStart(2, '0');
    const formattedTime = `${minutes}:${seconds}`;

    setUserTime(formattedTime);
    localStorage.setItem('userTime', formattedTime);
    setTimeEntered(true);
    localStorage.setItem('timeEntered', 'true');
    localStorage.setItem('date', currentDate);
  };

  const handleTimeInputError = (errorMessage) => {
    // Handle case where submission failed
    setError(errorMessage);
    // Don't update state - user can try again
  };

  return (
    <div className="container">
      <h1>NYT Crossword Comparison</h1>
      {!timeEntered ? (
        <div className="time-input">
          <TimeInput onTimeInput={handleTimeInput} onError={handleTimeInputError} />
          {error && <p className="error" role="alert">{error}</p>}
        </div>
      ) : (
        <>
          <p className="user-time" aria-live="polite">Your time: {userTime}</p>
          {isLoading ? (
            <p aria-live="polite">Loading chart data...</p>
          ) : error ? (
            <p aria-live="assertive" role="alert">{error}</p>
          ) : chartData.length > 0 ? (
            <div className="chart" aria-label="Histogram of crossword completion times">
              <div className="bar-chart">
                {chartData.map((item, index) => {
                  const maxCount = Math.max(...chartData.map(d => d.count));
                  const barWidth = (item.count / maxCount) * 100;
                  return (
                    <div key={index} className="bar-item">
                      <div className="bar-label">{item.range}</div>
                      <div className="bar-container">
                        <div
                          className="bar"
                          style={{ width: `${barWidth}%` }}
                          aria-label={`${item.range}: ${item.count} submissions`}
                        >
                          <span className="bar-count">{item.count}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
};

export default App;