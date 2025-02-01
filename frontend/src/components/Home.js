import React from "react";
import { Link, useNavigate } from "react-router-dom";
import SkincareImage from "../images/skincare.jpg"; // Import your image

function Home() {
  const navigate = useNavigate();

  const navigateToChatbot = () => {
    navigate("/Chatbot");
  };

  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.heroSection}>
        <div style={styles.heroContent}>
          <h1 style={styles.heroHeadline}>Your Smart Guide to Flawless Skin</h1>
          <p style={styles.heroSubtext}>
          Say goodbye to trial and error—AI picks the right products for 
          </p>
          <div style={styles.ctaButtons}>
            
            <button style={styles.ctaButton}>Lets Dive Into it</button>
          </div>
        </div>
        {/* Right-side Image */}
        <img src={SkincareImage} alt="Skincare Assistant" style={styles.heroImage} />
      </div>

      {/* Floating Chatbot Icon */}
      <div style={styles.botIcon} onClick={navigateToChatbot}>
        💬
      </div>
    </div>
  );
}

/* Updated CSS */
const styles = {
  container: {
    position: "relative",
    minHeight: "100vh",
    fontFamily: "Arial, sans-serif",
    textAlign: "center",
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    color: "#FFE6F2",
  },
  heroSection: {
    height: "100vh",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0 10%",
    backgroundSize: "cover",
    backgroundPosition: "center",
    textAlign: "left",
    position: "relative", // Add relative positioning to heroSection
  },
  
  heroContent: {
    maxWidth: "50%",
    position: "relative", // Ensure the overlay is applied to text
    zIndex: 2, // Make sure text appears above the overlay
  },
  
  overlay: {
    content: "",
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0, 0, 0, 0.4)", // Dark overlay for better text contrast
    zIndex: 1,
  },
  heroHeadline: {
    fontSize: "38px",
    fontWeight: "bold",
    marginBottom: "20px",
    fontFamily:"franklin"
  },
  heroSubtext: {
    fontSize: "18px",
    marginBottom: "30px",
    lineHeight: "1.5",
  },
  ctaButtons: {
    display: "flex",
    gap: "20px",
  },
  ctaButton: {
    backgroundColor: "black",
    color: "#fff",
    padding: "12px 30px",
    fontSize: "16px",
    fontWeight: "bold",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s, box-shadow 0.3s, transform 0.3s",
    marginLeft:"155px"
  },
  heroImage: {
    width: "45%", // Adjust size
    maxWidth: "650px",
    borderRadius: "30px", // Curvy edges
    marginLeft : "100px",
    boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.2)", // Soft shadow
  },
  botIcon: {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    fontSize: "25px",
    cursor: "pointer",
    backgroundColor: "black",
    padding: "12px",
    borderRadius: "50%",
    boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.3)",
    zIndex: 1000,
    transition: "transform 0.3s, box-shadow 0.3s",
  },
};

export default Home;
