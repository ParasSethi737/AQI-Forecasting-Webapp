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
        const STATION = '@10124';
        const FROM = '2024-12-27'; //only accepts date in YYYY-MM-DD format
        //const FROM = lastUpdatedDate ? new Date(lastUpdatedDate).toISOString().split('T')[0] : ''; //only accepts date in YYYY-MM-DD format
        const IST_OFFSET = 5.5; // India Standard Time (IST) UTC offset (UTC+5:30)
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
    try {
        console.log('Starting CSV update...');
        const lastUpdatedDate = await getLastUpdateDate();
        console.log('Last updated date:', lastUpdatedDate);

        const data = await fetchData(lastUpdatedDate);
        console.log('Fetched data:', data);

        if (data) {
            const response = await sendFetchedDataToServer(data);
            console.log('Data sent to server successfully:', response);
            displayCSV();
        }
    } catch (error) {
        console.error('Error updating CSV:', error);
    }
}

async function displayCSV() {
    try {
        console.log('Fetching cleaned_data.csv...');
        const response = await fetch('/datasets/cleaned_data.csv');
        const csvData = await response.text();
        document.getElementById('csvContent').textContent = csvData;
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

function renderForecastChart(days, predictions) {
    console.log('Rendering chart with days:', days, 'and predictions:', predictions);
    const ctx = document.getElementById('forecastChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [{
                label: 'Predicted AQI for the next 7 days',
                data: predictions,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
            }],
        },
        options: {
            scales: {
                y: { beginAtZero: false, title: { display: true, text: 'AQI' } },
            },
        },
    });
}

document.getElementById('fetchButton').addEventListener('click', updateCSV);
window.onload = getForecast;
