import React, { useState } from 'react';

function TimeInput() {
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(true);

  const handleInputChange = (event) => {
    const value = event.target.value;
    setInputValue(value);

    // Verify the input format
    const regex = /^[0-9]:[0-5][0-9]/;
    setIsValid(regex.test(value));
  };

  const handleVerify = () => {
    if (isValid) {
      console.log('Input is valid:', inputValue);
      // You can perform further actions with the valid input here
    } else {
      console.error('Invalid input:', inputValue);
    }
  };

  return (
    <div>
      <h1>Time Measurement Input</h1>
      <label>
        Enter Time (mm:ss):
        <input type="text" value={inputValue} onChange={handleInputChange} />
      </label>
      <button onClick={handleVerify}>Verify</button>
      {!isValid && <p style={{ color: 'red' }}>Invalid input format. Please use mm:ss format.</p>}
    </div>
  );
}

export default TimeInput;
