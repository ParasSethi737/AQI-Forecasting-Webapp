import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import './History.css'; // Import the CSS file

function History() {
  const [data, setData] = useState([]);
  const [tableName, setTableName] = useState('aqi_forecast'); // Default table name
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedColumn, setSelectedColumn] = useState(''); // For column-specific filtering

  // Debounce the search query
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300); // 300ms debounce delay

    return () => {
      clearTimeout(handler);
    };
  }, [searchQuery]);

  const fetchData = useCallback(async () => {
    if (!tableName) {
      console.error('Table name is required.');
      return;
    }

    try {
      let url = `https://aqi-forecasting-webapp-1.onrender.com/api/view-data/${tableName}`;
      if (startDate || endDate) {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        url += `?${params.toString()}`;
      }

      console.log('Request URL:', url); // Debugging: Log the constructed request URL

      const response = await axios.get(url, { headers: { Accept: 'application/json' } });

      console.log('Response Status:', response.status); // Debugging: Log the response status
      console.log('Response Headers:', response.headers); // Debugging: Log the response headers

      if (response.headers['content-type']?.includes('application/json')) {
        console.log('Raw data fetched from backend:', response.data); // Debugging: Log the raw data

        let fetchedData = response.data;

        // Ensure fetchedData is an array
        if (!Array.isArray(fetchedData)) {
          console.error('Fetched data is not an array:', fetchedData);
          fetchedData = []; // Fallback to an empty array
        }

        let dateKey = 'date';
        if (tableName === 'aqi_forecast') {
          dateKey = 'forecast_date';
        } else if (tableName === 'model_evaluation') {
          dateKey = 'timestamp';
        }

        // Process the fetched data
        fetchedData = fetchedData.map((row, index) => {
          const { [dateKey]: dateValue, ...rest } = row;
          const formattedDate = dateValue
            ? new Date(dateValue).toISOString().split('T')[0]
            : 'N/A';

          console.log(`Row ${index} - Date: ${formattedDate}, Data:`, rest); // Debugging: Log individual row data

          // Round all numerical values to 2 decimal places
          const roundedRow = {};
          for (const [key, value] of Object.entries(rest)) {
            if (typeof value === 'number') {
              roundedRow[key] = +value.toFixed(3);
            } else {
              roundedRow[key] = value;
            }
          }

          return {
            date: formattedDate,
            ...roundedRow,
          };
        });

        setData(fetchedData);
        console.log('Processed data:', fetchedData); // Debugging: Log the processed data
      } else {
        console.error('Unexpected response format:', response.data);
      }
    } catch (err) {
      console.error('Error fetching data:', err.message || err);
    }
  }, [tableName, startDate, endDate]);

  // Filter data based on the debounced search query and selected column
  const filteredData = data.filter((row) => {
    if (selectedColumn) {
      // Search in the selected column only
      return row[selectedColumn]?.toString().toLowerCase().includes(debouncedSearchQuery.toLowerCase());
    }
    // Search across all columns
    return Object.values(row).some((value) =>
      value?.toString().toLowerCase().includes(debouncedSearchQuery.toLowerCase())
    );
  });

  const columnNameMapping = { // Mapping for user friendly column names
    date: 'Date',
    aqi: 'AQI',
    aqi_pm25: 'AQI PM2.5',
    aqi_pm10: 'AQI PM10',
    aqi_co: 'AQI CO',
    aqi_no2: 'AQI NO2',
    aqi_o3: 'AQI O3',
    aqi_so2: 'AQI SO2',
    pm25: 'PM2.5 (µg/m³)',
    pm10: 'PM10 (µg/m³)',
    co: 'Carbon Monoxide (CO)',
    no2: 'Nitrogen Dioxide (NO2)',
    o3: 'Ozone (O3)',
    so2: 'Sulfur Dioxide (SO2)',
    conditions: 'Conditions',
    description: 'Description',
    cloudcover: 'Cloud Cover',
    dew: 'Dew Point',
    feelslike: 'Feels Like',
    feelslikemax: 'Feels Like (Max)',
    feelslikemin: 'Feels Like (Min)',
    humidity: 'Humidity (%)',
    temp: 'Temperature (°C)',
    tempmax: 'Max Temperature (°C)',
    tempmin: 'Min Temperature (°C)',
    timestamp: 'Timestamp',
    icon: 'Weather Icon',
    moonphase: 'Moon Phase',
    name: 'Location Name',
    precip: 'Precipitation (mm)',
    precipcover: 'Precipitation Cover (%)',
    precipprob: 'Precipitation Probability (%)',
    preciptype: 'Precipitation Type',
    sealevelpressure: 'Sea Level Pressure (hPa)',
    severerisk: 'Severe Risk',
    snow: 'Snow (mm)',
    snowdepth: 'Snow Depth (cm)',
    solarenergy: 'Solar Energy (kWh/m²)',
    solarradiation: 'Solar Radiation (W/m²)',
    stations: 'Weather Stations',
    sunrise: 'Sunrise Time',
    sunset: 'Sunset Time',
    uvindex: 'UV Index',
    visibility: 'Visibility (km)',
    winddir: 'Wind Direction (°)',
    windgust: 'Wind Gust (km/h)',
    windspeed: 'Wind Speed (km/h)',
    predicted_date: 'Predicted Date',
    predicted_aqi: 'Predicted AQI',
    model_name: 'Model Name',
    location: 'Location',
    mae: 'Mean Absolute Error',
    rmse: 'Root Mean Square Error',
    mape: 'Mean Absolute Percentage Error',
    r2: 'R² Score',
  };

  const predefinedColumnOrder = [
    'date', 'forecast_date', 'predicted_date', 'predicted_aqi', 'model_name', 'location',
    'pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
    'aqi_pm25', 'aqi_pm10', 'aqi_o3', 'aqi_no2', 'aqi_so2', 'aqi_co', 'aqi',
    'name', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike',
    'dew', 'humidity', 'precip', 'precipprob', 'precipcover', 'preciptype', 'snow', 'snowdepth',
    'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility',
    'solarradiation', 'solarenergy', 'uvindex', 'severerisk', 'sunrise', 'sunset',
    'moonphase', 'conditions', 'description', 'icon', 'stations',
    'timestamp', 'mae', 'rmse', 'mape', 'r2',
  ];

  return (
    <div style={{ padding: '1rem', maxWidth: '100%', overflow: 'hidden' }}>
      <h2 style={{ color: '#333', textAlign: 'center', marginBottom: '1rem' }}>Historical Data</h2>

      <div className="controls-container">
        <label>
          Table:
          <select value={tableName} onChange={(e) => setTableName(e.target.value)}>
            <option value="aqi_forecast">AQI Forecast</option>
            <option value="raw_data">Raw Data</option>
            <option value="cleaned_data">Cleaned Data</option>
            <option value="weather_data">Weather Data</option>
            <option value="pollutant_data">Pollutant Data</option>
            <option value="model_evaluation">Model Evaluation Metrics</option>
          </select>
        </label>

        <label>
          Start Date:
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>

        <label>
          End Date:
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>

        <label>
          Search:
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
          />
        </label>

        <label>
          Filter by Column:
          <select value={selectedColumn} onChange={(e) => setSelectedColumn(e.target.value)}>
            <option value="">All Columns</option>
            {data.length > 0 &&
              Object.keys(data[0]).map((key) => (
                <option key={key} value={key}>
                  {columnNameMapping[key] || key}
                </option>
              ))}
          </select>
        </label>

        <button onClick={fetchData}>Fetch Data</button>
      </div>

      <div className="table-container" style={{ '--highlight-column': selectedColumn ? Object.keys(data[0]).indexOf(selectedColumn) + 1 : 0 }}>
        {Array.isArray(data) && data.length > 0 ? (
          <table className={selectedColumn ? 'highlight-column' : ''}>
            <thead>
              <tr>
                {predefinedColumnOrder.map(
                  (key) =>
                    data[0]?.[key] !== undefined && ( // Only render columns that exist in the data
                      <th key={key}>{columnNameMapping[key] || key}</th>
                    )
                )}
              </tr>
            </thead>
            <tbody>
              {filteredData.map((row, i) => (
                <tr key={i}>
                  {predefinedColumnOrder.map(
                    (key) =>
                      row[key] !== undefined && ( // Only render columns that exist in the row
                        <td
                          key={key}
                          data-value={row[key]}
                          style={{
                            backgroundColor: selectedColumn === key ? '#475569' : 'inherit',
                            color: selectedColumn === key ? '#facc15' : 'inherit',
                            fontWeight: selectedColumn === key ? 'bold' : 'normal',
                          }}
                        >
                          {row[key]}
                        </td>
                      )
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#e2e8f0', textAlign: 'center' }}>No data found for the selected filters.</p>
        )}
      </div>
    </div>
  );
}

export default History;