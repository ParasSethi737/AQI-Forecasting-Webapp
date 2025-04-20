import React from 'react';
import { Link } from 'react-router-dom';
import styles from './NavBar.module.css';

function NavBar() {
  return (
    <nav className={styles.nav}>
      <Link to="/" className={styles.logo}>
        <h1>AQI Forecasting Webapp</h1>
      </Link>
      <ul className={styles.navLinks}>
        <li className={styles.navItem}>
          <Link to="/current">Current Conditions</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/forecast">Forecast</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/history">Historical Data</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/analytics">Analytics</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/contact">Contact</Link>
        </li>
      </ul>
    </nav>
  );
}

export default NavBar;