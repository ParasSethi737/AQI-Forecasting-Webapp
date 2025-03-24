async function getLastUpdateDate() {
    try {
        console.log('Fetching last update date...');
        const response = await fetch('/api/last_update_date');
        const data = await response.json();
        console.log('Last update date fetched:', data);
        return data.last_update_date;
    } catch (error) {
        console.error('Error fetching last updated date:', error);
        return null;
    }
}
async function fetchData(lastUpdatedDate) {
    try {
        console.log('Fetching API keys...');
        const response = await fetch('/api/get_keys');
        const keys = await response.json();
        console.log('API keys fetched:', keys);

        const WEATHER_KEY = keys.WEATHER_KEY;
        const POLLUTANT_KEY = keys.POLLUTANT_KEY;
        const STATION = '@10124'; //only accepts date in YYYY-MM-DD format
        const FROM = lastUpdatedDate ? new Date(lastUpdatedDate).toISOString().split('T')[0] : ''; //only accepts date in YYYY-MM-DD format
        const TO_raw = new Date().toLocaleString("en-US", { timeZone: `Asia/Kolkata` }).split('T')[0];
        const TO = new Date(TO_raw).toISOString().split('T')[0];
        console.log('FROM:', FROM, 'TO:', TO);

        console.log('Fetching pollutant data...');
        const pollutantResponse = await fetch(`https://api.waqi.info/feed/${STATION}/?token=${POLLUTANT_KEY}`);
        const pollutantData = await pollutantResponse.json();
        console.log('Pollutant data fetched:', pollutantData);

        console.log('Fetching weather data...');
        const weatherResponse = await fetch(`https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/INDIRA%20GANDHI%20INTERNATIONAL%2C%20IN/${FROM}/${TO}?unitGroup=metric&include=days&key=${WEATHER_KEY}&contentType=json`);
        const weatherData = await weatherResponse.json();
        console.log('Weather data fetched:', weatherData);

        // Iterate through all days and compile combined data
        let combinedResults = [];

        weatherData.days.forEach(day => {
            const combinedData = {
                date: day.datetime,
                pollutant: {
                    pm25: pollutantData.data.iaqi.pm25 ? pollutantData.data.iaqi.pm25.v : null,
                    pm10: pollutantData.data.iaqi.pm10 ? pollutantData.data.iaqi.pm10.v : null,
                    co: pollutantData.data.iaqi.co ? pollutantData.data.iaqi.co.v : null,
                    no2: pollutantData.data.iaqi.no2 ? pollutantData.data.iaqi.no2.v : null,
                    so2: pollutantData.data.iaqi.so2 ? pollutantData.data.iaqi.so2.v : null,
                    o3: pollutantData.data.iaqi.o3 ? pollutantData.data.iaqi.o3.v : null,
                    AQI: pollutantData.data.aqi,
                },
                weather: {
                    tempmax: day.tempmax,
                    tempmin: day.tempmin,
                    temp: day.temp,
                    humidity: day.humidity,
                    dew: day.dew,
                    windspeed: day.windspeed,
                    winddir: day.winddir,
                    windgust: day.windgust,
                    precip: day.precip,
                    cloudcover: day.cloudcover,
                    visibility: day.visibility,
                    pressure: day.pressure,
                },
            };

            combinedResults.push(combinedData);
        });

        return combinedResults;

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}


async function sendFetchedDataToServer(data) {
    try {
        console.log('Sending fetched data to server...', data);
        const response = await fetch('/update_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const result = await response.json();
        console.log('Server response:', result);
        return result;
    } catch (error) {
        console.error('Error running Python script:', error);
        document.getElementById('error-message').textContent = `An error occurred: ${error.message}`;
    }
}

async function updateCSV() {
    const lastUpdatedDate = await getLastUpdateDate();
    const data = await fetchData(lastUpdatedDate);
    if (data.length > 0) {
        await sendFetchedDataToServer(data);
        displayCSV();
        getForecast();
    } else {
        console.error('No data fetched.');
    }
}

document.getElementById('viewCsvButton').addEventListener('click', async () => {
    console.log("View CSV button clicked! Fetching CSV...");
    await displayCSV(); // Fetch and display CSV data

    // Manually show the modal (in case Bootstrap's auto-trigger fails)
    const csvModal = new bootstrap.Modal(document.getElementById('csvModal'));
    csvModal.show();
});

async function displayCSV() {
    try {
        const response = await fetch('/datasets/cleaned_data.csv');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const csvData = await response.text();
        console.log('Fetched CSV Data:', csvData);

        const csvContainer = document.getElementById('csvModalContent');
        if (!csvContainer) {
            console.error("Element 'csvModalContent' not found!");
            return;
        }

        csvContainer.textContent = csvData; // Display raw CSV
    } catch (error) {
        console.error('Error fetching CSV:', error);
    }
}

async function getForecast() {
    try {
        console.log('Fetching forecast...');
        const response = await fetch('/get_forecast');
        const forecastData = await response.json();
        console.log('Forecast data fetched:', forecastData);

        if (forecastData) {
            const days = Object.keys(forecastData);
            const predictions = Object.values(forecastData);
            console.log('Rendering forecast chart...');
            renderForecastChart(days, predictions);
        }
    } catch (error) {
        console.error('Error fetching forecast:', error);
    }
}
document.addEventListener("DOMContentLoaded", async () => {
    // Fetch weather and pollutant data and update UI
    const lastUpdatedDate = await getLastUpdateDate();
    const fetchedData = await fetchData(lastUpdatedDate);
    if (fetchedData) {
        displayFetchedData(fetchedData);
        const response = await sendFetchedDataToServer(fetchedData);
        if (response) {
            console.log('CSV updated successfully.');
            getForecast(); // Fetch and display forecast after CSV update
        }
    }
});

async function displayFetchedData(data) {
    const dataDisplay = document.getElementById("dataDisplay");
    dataDisplay.innerHTML = "";

    data.forEach(entry => {
        const { date, pollutant, weather } = entry;
        const currentDateTime = new Date(date).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });

        const card = document.createElement("div");
        card.className = "col-md-4 mb-4 d-flex align-items-stretch";
        card.innerHTML = `
            <div class="card h-100">
                <div class="card-header bg-secondary text-white">
                    <strong>${currentDateTime}</strong>
                </div>
                <div class="card-body d-flex flex-column">
                    <h5>Pollutant Data</h5>
                    <ul>
                        <li><i class="fas fa-smog"></i> AQI: ${pollutant.AQI || "N/A"}</li>
                        <li><i class="fas fa-cloud-sun-rain"></i> PM2.5: ${pollutant.pm25 || "N/A"}</li>
                        <li><i class="fas fa-cloud-sun-rain"></i> PM10: ${pollutant.pm10 || "N/A"}</li>
                        <li><i class="fas fa-burn"></i> CO: ${pollutant.co || "N/A"}</li>
                        <li><i class="fas fa-skull-crossbones"></i> NO2: ${pollutant.no2 || "N/A"}</li>
                        <li><i class="fas fa-sun"></i> SO2: ${pollutant.so2 || "N/A"}</li>
                        <li><i class="fas fa-cloud-moon"></i> O3: ${pollutant.o3 || "N/A"}</li>
                    </ul>
                    <h5>Weather Data</h5>
                    <ul>
                        <li><i class="fas fa-temperature-high"></i> Max Temp: ${weather.tempmax || "N/A"}°C</li>
                        <li><i class="fas fa-temperature-low"></i> Min Temp: ${weather.tempmin || "N/A"}°C</li>
                        <li><i class="fas fa-thermometer"></i> Temp: ${weather.temp || "N/A"}°C</li>
                        <li><i class="fas fa-tint"></i> Humidity: ${weather.humidity || "N/A"}%</li>
                        <li><i class="fas fa-cloud-showers-heavy"></i> Dew: ${weather.dew || "N/A"}°C</li>
                        <li><i class="fas fa-wind"></i> Wind Speed: ${weather.windspeed || "N/A"} km/h</li>
                        <li><i class="fas fa-compass"></i> Wind Direction: ${weather.winddir || "N/A"}</li>
                        <li><i class="fas fa-fan"></i> Wind Gust: ${weather.windgust || "N/A"} km/h</li>
                        <li><i class="fas fa-cloud-rain"></i> Precipitation: ${weather.precip || "N/A"} mm</li>
                        <li><i class="fas fa-cloud"></i> Cloud Cover: ${weather.cloudcover || "N/A"}%</li>
                        <li><i class="fas fa-eye"></i> Visibility: ${weather.visibility || "N/A"} km</li>
                        <li><i class="fas fa-tachometer-alt"></i> Pressure: ${weather.pressure || "N/A"} hPa</li>
                    </ul>
                </div>
            </div>
        `;
        dataDisplay.appendChild(card);
    });
}

let forecastChartInstance = null;

function renderForecastChart(dates, predictions) {
    const ctx = document.getElementById('forecastChart').getContext('2d');

    // Destroy existing chart if it exists
    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    // Create new chart instance and assign it to the global variable
    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Predicted AQI',
                data: predictions,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, position: 'top' },
                tooltip: { enabled: true },
            },
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'AQI' }, beginAtZero: false },
            },
        },
    });
}

document.addEventListener("DOMContentLoaded", updateCSV);

document.getElementById('fetchButton').addEventListener('click', updateCSV);
document.getElementById('viewCsvButton').addEventListener('click', displayCSV);

window.onload = getForecast;
