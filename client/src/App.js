import React from 'react';
import PrintDB from './components/printData';
import TimeInput from './components/TimeInput';
import { BarH } from "react-roughviz";

const App = () => {
  return (
    <div>
      <h1>Hello, React!</h1>
      <TimeInput />
      <PrintDB />
      <div class="viz"></div>
      <BarH
        data= {{
          labels: ['a', 'b'],
          values: [10, 20]
        }}
    />
    </div>
  );
};

export default App;
