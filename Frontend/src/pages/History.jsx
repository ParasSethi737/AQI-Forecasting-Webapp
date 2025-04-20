import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import './history.css'; // Import the CSS file

function History() {
  const [data, setData] = useState([]);
  const [tableName, setTableName] = useState('AQIForecast');
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
      console.log('Fetching data...');
      let url = `http://localhost:5000/api/view-data/${tableName}`;
      if (startDate || endDate) {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        url += `?${params.toString()}`;
      }

      console.log('Request URL:', url);

      const response = await axios.get(url, { headers: { Accept: 'application/json' } });
      if (response.headers['content-type']?.includes('application/json')) {
        console.log('Raw data fetched from backend:', response.data); // Debugging log
        let fetchedData = response.data;

        // Ensure fetchedData is an array
        if (!Array.isArray(fetchedData)) {
          console.error('Fetched data is not an array:', fetchedData);
          fetchedData = []; // Fallback to an empty array
        }

        const dateKey = tableName === 'AQIForecast' ? 'forecast_date' : 'date';
        // Reorder columns and format the date/forecast_date
        fetchedData = fetchedData.map((row) => {
          const { [dateKey]: dateValue, ...rest } = row;
          const formattedDate = dateValue
            ? dateValue.split(' ')[0]
            : 'N/A';
          return {
            date: formattedDate, // Add the formatted date as the first column
            ...rest, // Spread the remaining columns
          };
        });

        setData(fetchedData);
        console.log('Processed data:', fetchedData); // Debugging log
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
  };

  const predefinedColumnOrder = [
    'date', 'forecast_date', 'predicted_date', 'predicted_aqi', 'model_name', 'location',
    'pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
    'aqi_pm25', 'aqi_pm10', 'aqi_o3', 'aqi_no2', 'aqi_so2', 'aqi_co', 'aqi',
    'name', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike',
    'dew', 'humidity', 'precip', 'precipprob', 'precipcover', 'preciptype', 'snow', 'snowdepth',
    'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility',
    'solarradiation', 'solarenergy', 'uvindex', 'severerisk', 'sunrise', 'sunset',
    'moonphase', 'conditions', 'description', 'icon', 'stations'
  ];

  return (
    <div style={{ padding: '1rem', maxWidth: '100%', overflow: 'hidden' }}>
      <h2 style={{ color: '#333', textAlign: 'center', marginBottom: '1rem' }}>Historical Data</h2>
  
      <div className="controls-container">
        <label>
          Table:
          <select value={tableName} onChange={(e) => setTableName(e.target.value)}>
            <option value="AQIForecast">AQIForecast</option>
            <option value="RawData">RawData</option>
            <option value="CleanedData">CleanedData</option>
            <option value="WeatherData">WeatherData</option>
            <option value="PollutantData">PollutantData</option>
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