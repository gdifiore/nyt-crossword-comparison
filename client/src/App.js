import React from 'react';
import PrintDB from './components/printData';
import TimeInput from './components/TimeInput';
//import Chart from './components/Chart'
import chartXkcd from 'chart.xkcd';
import { Bar } from "chart.xkcd-react"

const App = () => {
  return (
    <div>
      <h1>Hello, React!</h1>
      <TimeInput />
      <PrintDB />
      <Bar
        config={{
          title: 'github stars VS patron number', // optional
          // xLabel: '', // optional
          // yLabel: '', // optional
          data: {
            labels: ['github stars', 'patrons'],
            datasets: [{
              data: [100, 2],
            }],
          },
          options: { // optional
            yTickCount: 2,
          },
        }}
      />
    </div>
  );
};

export default App;
