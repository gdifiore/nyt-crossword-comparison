import React, { useState, useEffect } from 'react';
import TimeInput from './components/TimeInput';
import { BarH } from "react-roughviz";

import './App.css';

const App = () => {
  const storedDate = localStorage.getItem('date');
  const currentDate = new Date().toISOString().split('T')[0]; // Get the current date in YYYY-MM-DD format

  const [chartData, setChartData] = useState([]);
  const [timeEntered, setTimeEntered] = useState(storedDate === currentDate && localStorage.getItem('timeEntered') === 'true');
  const [userTime, setUserTime] = useState(localStorage.getItem('userTime'));

  useEffect(() => {
    if (timeEntered) {
      fetch('/api/chartData')
        .then(response => response.json())
        .then(data => setChartData(data.data));
    }
  }, [timeEntered]);

  const handleTimeInput = (time) => {
    const formattedTime = `${Math.floor(time / 60)}:${time % 60 < 10 ? '0' : ''}${time % 60}`; // Convert seconds to m:ss format
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
          <p className="user-time">Your time: {userTime}</p>
          {chartData.length > 0 && (
            <div className="chart">
              <BarH
                data={{
                  labels: chartData.map(item => item.range),
                  values: chartData.map(item => item.count)
                }}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default App;