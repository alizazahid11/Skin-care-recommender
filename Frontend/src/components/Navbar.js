import React from 'react';
import { NavLink } from 'react-router-dom'; // Use NavLink for active link functionality
import './Navbar.css';
import logo from '../images/Logo.png'; // Adjust path based on your folder structure


const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-logo">
        <img src={logo} alt="Logo" /> {/* Use imported logo */}
        </NavLink>
        <ul className="navbar-links">
          <li>
            <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink>
          </li>
          <li>
            <NavLink to="/comparison" className={({ isActive }) => isActive ? 'active' : ''}>Comparison</NavLink>
          </li>
          <li>
            <NavLink to="/recommendation" className={({ isActive }) => isActive ? 'active' : ''}>Recommendation</NavLink>
          </li>
          <li>
            <NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>About Us</NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;