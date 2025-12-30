import React, { useState } from 'react';
import '../App.css';

function TimeInput({ onTimeInput, onError }) {
  const [inputValue, setInputValue] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateTime = (value) => {
    // Basic format validation: m:ss or mm:ss
    const regex = /^([0-9]|[0-5][0-9]):[0-5][0-9]$/;
    if (!regex.test(value)) {
      return { valid: false, message: 'Invalid format. Use m:ss or mm:ss (e.g., 1:23 or 12:34)' };
    }

    // Parse time
    const [minutes, seconds] = value.split(':');
    const totalSeconds = parseInt(minutes, 10) * 60 + parseInt(seconds, 10);

    // Reject 0:00
    if (totalSeconds === 0) {
      return { valid: false, message: 'Invalid time! Please enter a valid completion time.' };
    }

    // Reject unrealistically fast times (under 10 seconds)
    if (totalSeconds < 10) {
      return { valid: false, message: "Too fast! Times under 10 seconds aren't valid for NYT Mini." };
    }

    // Reject times over 15 minutes (900 seconds)
    if (totalSeconds > 900) {
      return { valid: false, message: 'Too slow! Are you sure it took over 15 minutes? Please double-check your time.' };
    }

    return { valid: true, totalSeconds };
  };

  const handleInputChange = (event) => {
    const value = event.target.value;
    setInputValue(value);

    // Simple format check for immediate feedback
    const regex = /^([0-9]|[0-5][0-9]):[0-5][0-9]$/;
    setIsValid(regex.test(value));
    setErrorMessage('');
  };

  const handleVerify = async () => {
    // Comprehensive validation
    const validation = validateTime(inputValue);

    if (!validation.valid) {
      setIsValid(false);
      setErrorMessage(validation.message);
      return;
    }

    const totalSeconds = validation.totalSeconds;

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const response = await fetch('/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ secondsToComplete: totalSeconds })
      });

      const data = await response.json();

      if (!response.ok) {
        // Server returned an error - use error message from server if available
        throw new Error(data.error || 'Failed to submit time');
      }

      // Success - notify parent component
      setIsSuccess(true);
      setErrorMessage('');

      // Show success message briefly before transitioning
      setTimeout(() => {
        onTimeInput(totalSeconds);
      }, 800);
    } catch (error) {
      console.error('Error submitting time:', error);
      const errorMsg = error.message || 'Failed to submit time. Please try again.';
      setErrorMessage(errorMsg);

      // Notify parent component of error
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isSubmitting) {
      handleVerify();
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
          onKeyPress={handleKeyPress}
          aria-invalid={!isValid}
          aria-describedby="time-input-error time-input-hint"
          disabled={isSubmitting || isSuccess}
          placeholder="e.g., 1:23 (between 0:10 and 15:00)"
        />
      </label>
      <button
        onClick={handleVerify}
        disabled={!isValid || !inputValue || isSubmitting || isSuccess}
        aria-label="Submit time"
      >
        {isSuccess ? 'Submitted!' : isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
      {isSuccess && (
        <p id="time-input-success" style={{ color: 'green', fontWeight: 'bold' }} role="status" aria-live="polite">
          Time submitted successfully! Loading your results...
        </p>
      )}
      {errorMessage && <p id="time-input-error" style={{ color: 'red' }} role="alert">{errorMessage}</p>}
      <p id="time-input-hint" style={{ fontSize: '0.9em', color: '#666', marginTop: '0.5em' }}>
        Please enter a time between 0:10 and 15:00
      </p>
    </div>
  );
}

export default TimeInput;