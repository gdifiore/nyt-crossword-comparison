import React, { useState } from 'react';
import '../App.css';

function TimeInput({ onTimeInput }) {
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  const handleInputChange = (event) => {
    const value = event.target.value;
    setInputValue(value);

    const regex = /^([0-9]|[0-5][0-9]):[0-5][0-9]$/;
    setIsValid(regex.test(value));
  };

  const handleVerify = () => {
    if (isValid) {
      const [minutes, seconds] = inputValue.split(':');
      const totalSeconds = parseInt(minutes) * 60 + parseInt(seconds);

      fetch('/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ secondsToComplete: totalSeconds })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Response:', data);
          onTimeInput(totalSeconds);
          setErrorMessage('');
        })
        .catch(error => {
          console.error('Error:', error);
          setErrorMessage('Failed to submit time. Please try again.');
        });
    } else {
      setErrorMessage('Invalid input format. Please use the m:ss or mm:ss format.');
    }
  };

  return (
    <div className="time-input">
      <label htmlFor="time-input">
        Enter Your Time (m:ss or mm:ss):
        <input
          id="time-input"
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          aria-invalid={!isValid}
          aria-describedby="time-input-error"
        />
      </label>
      <button onClick={handleVerify} aria-label="Submit time">Submit</button>
      {errorMessage && <p id="time-input-error" style={{ color: 'red' }}>{errorMessage}</p>}
    </div>
  );
}

export default TimeInput;