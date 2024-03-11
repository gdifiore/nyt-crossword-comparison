import React, { useState, useEffect } from 'react';

const DataComponent = () => {
  const [apiData, setApiData] = useState(null);

  useEffect(() => {
    // Fetch data from Flask API
    fetch('/api/data')
      .then(response => response.json())
      .then(data => {
        // Set the fetched data in the state
        setApiData(data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  return (
    <div>
      <h1>Data Component</h1>
      {apiData && (
        <div>
          <h2>API Data:</h2>
          <pre>{JSON.stringify(apiData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default DataComponent;
