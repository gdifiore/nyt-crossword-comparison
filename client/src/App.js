import React, { useState, useEffect } from 'react';
import TimeInput from './components/TimeInput';
import { BarH } from "react-roughviz";

const App = () => {
  const storedDate = localStorage.getItem('date');
  const currentDate = new Date().toISOString().split('T')[0]; // Get the current date in YYYY-MM-DD format

  const [chartData, setChartData] = useState([]);
  const [timeEntered, setTimeEntered] = useState(storedDate === currentDate && localStorage.getItem('timeEntered') === 'true');

  useEffect(() => {
    if (timeEntered) {
      fetch('/api/chartData')
        .then(response => response.json())
        .then(data => setChartData(data.data));
    }
  }, [timeEntered]);

  const handleTimeInput = (time) => {
    setTimeEntered(true);
    localStorage.setItem('timeEntered', 'true');
    localStorage.setItem('date', currentDate);
  };

  return (
    <div>
      <h1>Hello, React!</h1>
      {!timeEntered ? (
        <TimeInput onTimeInput={handleTimeInput} />
      ) : chartData.length > 0 && (
        <BarH
          data={{
            labels: chartData.map(item => item.range),
            values: chartData.map(item => item.count)
          }}
        />
      )}
    </div>
  )
};

export default App;