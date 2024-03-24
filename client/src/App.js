import React from 'react';
import PrintDB from './components/printData';
import TimeInput from './components/TimeInput';

const App = () => {
  return (
    <div>
      <h1>Hello, React!</h1>
      <TimeInput />
      <PrintDB />
    </div>
  );
};

export default App;
