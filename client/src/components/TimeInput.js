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

      const [minutes, seconds] = inputValue.split(':');
      const totalSeconds = parseInt(minutes) * 60 + parseInt(seconds);
      console.log('Converted to seconds:', totalSeconds);

      // log to db
      fetch('/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ secondsToComplete: totalSeconds })
      })
        .then(response => response.json())
        .then(data => {
          // handle the response data
          console.log('Response:', data);
        })
        .catch(error => {
          console.error('Error:', error);
        });
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
