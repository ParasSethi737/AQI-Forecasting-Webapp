import React, { useEffect, useState } from 'react';
import './Landing.css';
import axios from 'axios';

function LandingPage() {
    const [evaluationMetrics, setEvaluationMetrics] = useState(null);

    useEffect(() => {
        async function fetchEvaluationMetrics() {
            try {
                const response = await axios.get(`https://aqi-forecasting-webapp-1.onrender.com/api/get_evaluation_metrics`);
                console.log('Evaluation metrics:', response.data);
                const metrics = response.data.data[0]; 
                setEvaluationMetrics({
                    timestamp: metrics.timestamp,
                    mae: metrics.mae.toFixed(3),
                    r2: metrics.r2.toFixed(3),
                    rmse: metrics.rmse.toFixed(3),
                    mape: (metrics.mape * 100).toFixed(3), // Convert MAPE to percentage and format
                });
            } catch (error) {
                console.error('Error fetching evaluation metrics:', error);
            }
        }
        fetchEvaluationMetrics();
    }, []);

    return (
        <div className="landing-page-container">
            <h1 className="main-title">AQI Forecasting Web App</h1>
            <p className="subtitle">
                A robust machine learning system for real-time AQI prediction, backed by automation and modern DevOps tooling
            </p>

            <div className="card-container">
                <section className="highlight-card">
                    <h2>Project Overview</h2>
                    <p>
                        This web application forecasts the Air Quality Index (AQI) in Delhi for the upcoming 7 days.
                         It uses over <strong>10 years</strong> of historical data and real-time updates to ensure consistent and adaptive forecasting.
                          Designed as a full-stack solution, the app includes a daily data pipeline, automated retraining, and a dynamic user interface.
                    </p>
                </section>

                <section className="highlight-card">
                    <h2>Model Design & Training</h2>
                    <p>
                        My forecasting model is <strong>XGBoost</strong> — the best performer among models like Random Forest, LightGBM, and CatBoost — trained on <strong>10 years of historical pollutant and weather data</strong> for Delhi.
                         Extensive exploratory data analysis (EDA) and correlation studies were conducted to understand the data and guide feature engineering. Features were thoughtfully engineered and rigorously tested to ensure robust and accurate predictions.
                          The model was then carefully optimized using grid search. Missing data and outliers were handled meticulously during preprocessing. The model’s performance was validated using cross-validation and evaluated through metrics such as RMSE and R² to guarantee reliability.
                    </p>
                    {evaluationMetrics ? (
                        <ul>
                            <li><strong>Forecast Horizon:</strong> 7-day ahead AQI prediction</li>
                            <li><strong>Feature Engineering:</strong> pollutant cumulative sums, interaction terms (e.g., PM2.5 × CO, temperature × humidity), seasonal indicators (summer/winter flags), and total pollution aggregation</li>
                            <li><strong>Lag Features:</strong> AQI values from the previous 7 days to capture temporal dependencies via autoregression</li>
                            <li>
                            <strong>Latest Evaluation Metrics</strong> (
                                <strong>Created at:</strong> {
                                new Date(evaluationMetrics.timestamp).toLocaleString('en-GB', {
                                day: 'numeric',
                                month: 'numeric',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                                })
                            }):
                            <ul>
                                <li><strong>R²:</strong> {evaluationMetrics.r2}</li>
                                <li><strong>MAE:</strong> {evaluationMetrics.mae}</li>
                                <li><strong>RMSE:</strong> {evaluationMetrics.rmse}</li>
                                <li><strong>MAPE:</strong> {evaluationMetrics.mape}%</li>
                            </ul>
                            </li>
                            <li><strong>Train/Test Split:</strong> 80/20 with chronological ordering to simulate future forecasting</li>
                            <li><strong>Model Persistence:</strong> Saved using <code>joblib</code> for efficient reuse</li>
                        </ul>
                    ) : (
                        <p>Loading evaluation metrics...</p>
                    )}
                </section>

                <section className="highlight-card">
                    <h2>Tech Stack</h2>
                    <ul>
                        <li><strong style={{ color: '#4ecdc4' }}>Frontend:</strong> React.js, Chart.js for dynamic AQI visualization</li>
                        <li><strong style={{ color: '#4ecdc4' }}>Backend:</strong> Flask (REST APIs), PostgreSQL</li>
                        <li><strong style={{ color: '#4ecdc4' }}>Machine Learning:</strong> XGBoost, Scikit-learn, Pandas, NumPy</li>
                        <li><strong style={{ color: '#4ecdc4' }}>DevOps:</strong> Docker, GitHub Actions for CI/CD and automated retraining</li>
                    </ul>
                </section>

                <section className="highlight-card">
                    <h2>Data & ML Pipeline</h2>
                    <ul>
                        <li><strong>Pollutant Data:</strong> Sourced from the <a href="https://waqi.info" target="_blank" rel="noopener noreferrer">World Air Quality Index (WAQI)</a></li>
                        <li><strong>Weather Data:</strong> Pulled via <a href="https://www.visualcrossing.com/" target="_blank" rel="noopener noreferrer">Visual Crossing API</a></li>
                        <li><strong>Pipeline:</strong> Hourly data fetching → Data cleaning → Feature engineering → Database storage</li>
                        <li><strong>Forecast Generation:</strong> Daily model retraining → Hourly forecast updates</li>
                    </ul>
                </section>

                <section className="highlight-card cta">
                    <h2>Try It Out</h2>
                    <a href="/forecast" className="cta-button">View Forecast</a>
                </section>
            </div>
        </div>
    );
}


export default LandingPage;
