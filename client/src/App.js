import React, { useState, useEffect } from 'react';
import PrintDB from './components/PrintData';
import TimeInput from './components/TimeInput';
import { BarH } from "react-roughviz";

const App = () => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetch('/api/chartData')
      .then(response => response.json())
      .then(data => setChartData(data.data));
  }, []);

  return (
    <div>
      <h1>Hello, React!</h1>
      <TimeInput />
      {chartData.length > 0 && (
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
