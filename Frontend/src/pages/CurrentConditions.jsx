import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CurrentConditions.css'; // Ensure to import your custom CSS file

function CurrentConditions() {
  const [weatherData, setWeatherData] = useState(null);
  const [pollutantData, setPollutantData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetching data from the backend API
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL;

    axios.get(`${apiUrl}/api/fetch_current_data`) 
      .then((response) => {
        setWeatherData(response.data.weather_data[0]);
        setPollutantData(response.data.pollutant_data[0]);
        setLoading(false);
        console.log(response);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="current-conditions">
      <h2>Current Conditions</h2>
  
      <div className="grid-container">
        {/* Location and Date Information */}
        <div className="card location-card">
          <h3>Location and Date</h3>
          <p><strong>Location:</strong> {weatherData.name}</p>
          <p><strong>Date:</strong> {weatherData.date}</p>
          <p><strong>Conditions:</strong> {weatherData.conditions}</p>
        </div>

        {/* Temperature Information */}
        <div className="card temperature-card">
          <h3>Temperature Information</h3>
          <p><strong>Temperature:</strong> {weatherData.temp}°C</p>
          <p><strong>Feels Like:</strong> {weatherData.feelslike}°C</p>
          <p><strong>Max Temp:</strong> {weatherData.tempmax}°C</p>
          <p><strong>Min Temp:</strong> {weatherData.tempmin}°C</p>
        </div>

        {/* Pollutant Data */}
        <div className="card pollutant-card">
          <h3>Pollutant Data</h3>
          <p><strong>PM2.5:</strong> {pollutantData.pm25} µg/m³</p>
          <p><strong>PM10:</strong> {pollutantData.pm10} µg/m³</p>
          <p><strong>O3 (Ozone):</strong> {pollutantData.o3} µg/m³</p>
          <p><strong>NO2 (Nitrogen Dioxide):</strong> {pollutantData.no2} µg/m³</p>
          <p><strong>SO2 (Sulfur Dioxide):</strong> {pollutantData.so2} µg/m³</p>
          <p><strong>CO (Carbon Monoxide):</strong> {pollutantData.co} µg/m³</p>
          <p><strong>AQI:</strong> {pollutantData.AQI}</p>
        </div>

        {/* Wind Information */}
        <div className="card wind-card">
          <h3>Wind Information</h3>
          <p><strong>Wind Speed:</strong> {weatherData.windspeed} km/h</p>
          <p><strong>Wind Gust:</strong> {weatherData.windgust} km/h</p>
          <p><strong>Wind Direction:</strong> {weatherData.winddir}°</p>
        </div>

        {/* Precipitation and Cloud Information */}
        <div className="card precipitation-card">
          <h3>Precipitation and Cloud Information</h3>
          <p><strong>Precipitation:</strong> {weatherData.precip} mm</p>
          <p><strong>Precipitation Probability:</strong> {weatherData.precipprob}%</p>
          <p><strong>Snow:</strong> {weatherData.snow} mm</p>
          <p><strong>Snow Depth:</strong> {weatherData.snowdepth} cm</p>
          <p><strong>Cloud Cover:</strong> {weatherData.cloudcover}%</p>
          <p><strong>Visibility:</strong> {weatherData.visibility} km</p>
          <p><strong>Severe Risk:</strong> {weatherData.severerisk}</p>
          <p><strong>Humidity:</strong> {weatherData.humidity}%</p>
        </div>

        {/* Atmospheric and Solar Data */}
        <div className="card atmospheric-card">
          <h3>Atmospheric and Solar Data</h3>
          <p><strong>Dew Point:</strong> {weatherData.dew}°C</p>
          <p><strong>Sea Level Pressure:</strong> {weatherData.sealevelpressure} hPa</p>
          <p><strong>UV Index:</strong> {weatherData.uvindex}</p>
          <p><strong>Solar Energy:</strong> {weatherData.solarenergy} kWh/m²</p>
          <p><strong>Solar Radiation:</strong> {weatherData.solarradiation} W/m²</p>
          <p><strong>Sunrise:</strong> {weatherData.sunrise}</p>
          <p><strong>Sunset:</strong> {weatherData.sunset}</p>
          <p><strong>Moon Phase:</strong> {weatherData.moonphase}</p>
        </div>
      </div>
    </div>
  );
}

export default CurrentConditions;