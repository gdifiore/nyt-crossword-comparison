import React, { useState } from 'react';

function TimeInput() {
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(true);

  const handleInputChange = (event) => {
    const value = event.target.value;
    setInputValue(value);

    // verify the input format
    const regex = /^[0-9]:[0-5][0-9]/;
    setIsValid(regex.test(value));
  };

  const handleVerify = () => {
    if (isValid) {
      console.log('Input is valid:', inputValue);
      // log to db
      // switch website state to prevent input
    } else {
      console.error('Invalid input:', inputValue);
    }
  };

  return (
    <div>
      <h1>Time Measurement Input</h1>
      <label>
        Enter Time (m:ss):
        <input type="text" value={inputValue} onChange={handleInputChange} />
      </label>
      <button onClick={handleVerify}>Submit</button>
      {!isValid && <p style={{ color: 'red' }}>Invalid input format. Please use the m:ss format from the NYT mini crossword results.</p>}
    </div>
  );
}

export default TimeInput;
