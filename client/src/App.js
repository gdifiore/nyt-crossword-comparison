import React, { useState, useEffect } from 'react';
import TimeInput from './components/TimeInput';
import { BarH } from "react-roughviz";

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
      setIsLoading(true);
      fetch('/api/chartData')
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
          console.error('Error fetching chart data:', error);
          setError('Failed to load chart data. Please try again later.');
          setIsLoading(false);
        });
    }
  }, [timeEntered]);

  const handleTimeInput = (time) => {
    const formattedTime = `${Math.floor(time / 60)}:${time % 60 < 10 ? '0' : ''}${time % 60}`;
    setUserTime(formattedTime);
    localStorage.setItem('userTime', formattedTime);
    setTimeEntered(true);
    localStorage.setItem('timeEntered', 'true');
    localStorage.setItem('date', currentDate);
  };

  return (
    <div className="container">
      <h1>NYT Crossword Comparison</h1>
      {!timeEntered ? (
        <div className="time-input">
          <TimeInput onTimeInput={handleTimeInput} />
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
              <BarH
                data={{
                  labels: chartData.map(item => item.range),
                  values: chartData.map(item => item.count)
                }}
                responsive={true}
              />
            </div>
          ) : null}
        </>
      )}
    </div>
  );
};

export default App;