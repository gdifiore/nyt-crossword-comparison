// GetDataComponent.js
import React, { useState, useEffect } from 'react';

const GetData = () => {
  const [data, setData] = useState('');

  useEffect(() => {
    // Fetch data from the '/api/getData' route
    fetch('/api/getData')
      .then(response => response.json())
      .then(data => {
        // Set the fetched data in the state
        setData(data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  return (
    <div>
      <h2>Get Data</h2>
      {data && (
        <div>
          <h3>Fetched Data:</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default GetData;
