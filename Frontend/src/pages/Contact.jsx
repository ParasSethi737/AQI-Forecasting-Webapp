import React from 'react';
import './Contact.css';

function Contact() {
  return (
    <div className="contact-container">
      <h2 className="contact-heading">Contact</h2>
      <p className="contact-paragraph">
        Welcome to my AQI forecasting web app! Explore the app and check out my {' '}
        <a
          href="https://github.com/ParasSethi737"
          target="_blank"
          rel="noopener noreferrer"
          className="contact-link"
        >
          GitHub
        </a>.
      </p>
    </div>
  );
}

export default Contact;