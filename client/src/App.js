import React, { useState, useEffect } from 'react';
import TimeInput from './components/TimeInput';

import './App.css';

// Helper function to get stored time data from localStorage
const getStoredTimeData = () => {
  const storedDate = localStorage.getItem('date');
  const timeEntered = localStorage.getItem('timeEntered');
  const userTime = localStorage.getItem('userTime');

  return {
    storedDate,
    timeEntered: timeEntered === 'true',
    userTime
  };
};

const App = () => {
  const currentDate = new Date().toISOString().split('T')[0];
  const storedData = getStoredTimeData();

  // Clear old localStorage data if date has changed
  if (storedData.storedDate && storedData.storedDate !== currentDate) {
    localStorage.removeItem('timeEntered');
    localStorage.removeItem('userTime');
    localStorage.removeItem('userTimeInSeconds');
    localStorage.removeItem('date');
  }

  const [chartData, setChartData] = useState([]);
  const [timeEntered, setTimeEntered] = useState(storedData.storedDate === currentDate && storedData.timeEntered);
  const [userTime, setUserTime] = useState(storedData.storedDate === currentDate ? storedData.userTime : null);
  const [userTimeInSeconds, setUserTimeInSeconds] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

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
    setUserTimeInSeconds(time);
    localStorage.setItem('userTime', formattedTime);
    localStorage.setItem('userTimeInSeconds', time.toString());
    setTimeEntered(true);
    localStorage.setItem('timeEntered', 'true');
    localStorage.setItem('date', currentDate);
  };

  const handleTimeInputError = (errorMessage) => {
    // Handle case where submission failed
    setError(errorMessage);
    // Don't update state - user can try again
  };

  const handleResetTime = () => {
    setShowResetConfirm(true);
  };

  const confirmReset = () => {
    localStorage.removeItem('timeEntered');
    localStorage.removeItem('userTime');
    localStorage.removeItem('userTimeInSeconds');
    localStorage.removeItem('date');
    setTimeEntered(false);
    setUserTime(null);
    setUserTimeInSeconds(null);
    setChartData([]);
    setError(null);
    setShowResetConfirm(false);
  };

  const cancelReset = () => {
    setShowResetConfirm(false);
  };

  // Calculate percentile if we have user time and chart data
  const calculatePercentile = () => {
    if (!userTimeInSeconds || chartData.length === 0) return null;

    let fasterCount = 0;
    let totalCount = 0;

    chartData.forEach(bin => {
      const [low, high] = bin.range.split('-').map(timeStr => {
        const [min, sec] = timeStr.split(':').map(Number);
        return min * 60 + sec;
      });

      totalCount += bin.count;

      // If the bin is entirely faster than user's time
      if (high <= userTimeInSeconds) {
        fasterCount += bin.count;
      }
      // If user's time falls within this bin, count half (approximation)
      else if (low <= userTimeInSeconds && userTimeInSeconds <= high) {
        fasterCount += Math.floor(bin.count / 2);
      }
    });

    if (totalCount === 0) return null;

    const percentile = Math.round((fasterCount / totalCount) * 100);
    return 100 - percentile; // Flip to show "faster than X%"
  };

  // Determine if a bin contains the user's time
  const isUserBin = (binRange) => {
    if (!userTimeInSeconds) return false;

    const [low, high] = binRange.split('-').map(timeStr => {
      const [min, sec] = timeStr.split(':').map(Number);
      return min * 60 + sec;
    });

    return low <= userTimeInSeconds && userTimeInSeconds <= high;
  };

  // Load user time in seconds from localStorage on mount
  useEffect(() => {
    const storedSeconds = localStorage.getItem('userTimeInSeconds');
    if (storedSeconds) {
      setUserTimeInSeconds(parseInt(storedSeconds, 10));
    }
  }, []);

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
          <div className="results-header">
            <p className="user-time" aria-live="polite">Your time: {userTime}</p>
            <button className="reset-button" onClick={handleResetTime}>
              Change my time
            </button>
          </div>

          {showResetConfirm && (
            <div className="reset-confirm" role="dialog" aria-labelledby="reset-title">
              <h3 id="reset-title">Are you sure?</h3>
              <p>This will clear your submitted time and let you enter a new one.</p>
              <div className="reset-confirm-buttons">
                <button onClick={confirmReset} className="confirm-yes">Yes, reset</button>
                <button onClick={cancelReset} className="confirm-no">Cancel</button>
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="loading-container" aria-live="polite">
              <div className="skeleton-chart">
                <div className="skeleton-bar"></div>
                <div className="skeleton-bar"></div>
                <div className="skeleton-bar"></div>
                <div className="skeleton-bar"></div>
                <div className="skeleton-bar"></div>
              </div>
              <p>Loading chart data...</p>
            </div>
          ) : error ? (
            <p aria-live="assertive" role="alert" className="error">{error}</p>
          ) : chartData.length > 0 ? (
            <>
              <div className="chart" aria-label="Histogram of crossword completion times">
                <div className="bar-chart">
                  {chartData.map((item, index) => {
                    const maxCount = Math.max(...chartData.map(d => d.count));
                    const barWidth = (item.count / maxCount) * 100;
                    const isHighlighted = isUserBin(item.range);
                    return (
                      <div key={index} className="bar-item">
                        <div className="bar-label">{item.range}</div>
                        <div className="bar-container">
                          <div
                            className={`bar ${isHighlighted ? 'user-bar' : ''}`}
                            style={{ width: `${barWidth}%` }}
                            aria-label={`${item.range}: ${item.count} submissions${isHighlighted ? ' (your time is in this range)' : ''}`}
                          >
                            <span className="bar-count">{item.count}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
              {calculatePercentile() !== null && (
                <p className="percentile-info" aria-live="polite">
                  You were faster than {calculatePercentile()}% of solvers today!
                </p>
              )}
              <p className="timezone-info">
                Times reset daily at midnight UTC. Your local time: {new Date().toLocaleTimeString()}
              </p>
            </>
          ) : null}
        </>
      )}
    </div>
  );
};

export default App;