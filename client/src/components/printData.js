import React, { useState, useEffect } from 'react';

function PrintDB() {
  const [times, setTimes] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/printDB');
      const data = await response.json();
      setTimes(data.times);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div>
      <h1>Times from Database</h1>
      <ul>
        {times.map((time, index) => (
          <li key={index}>{`Index: ${time[0]}, Time: ${time[1]}`}</li>
        ))}
      </ul>
    </div>
  );
}

export default PrintDB;
