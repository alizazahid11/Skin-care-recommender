import React from 'react';
import { FaInstagram, FaLinkedin, FaGithub } from 'react-icons/fa';

const teamMembers = [
  { name: 'Ramsha Tariq', desc: 'Developed the BERT model for sentiment analysis, performed web scraping, and contributed to LSTM model development.', img: 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/a3336bb3-5de8-4f45-be4e-997b9b0c1f18/d9bkg0l-ccb01679-07f2-41fb-b53a-f7e09d4fe77e.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2EzMzM2YmIzLTVkZTgtNGY0NS1iZTRlLTk5N2I5YjBjMWYxOFwvZDlia2cwbC1jY2IwMTY3OS0wN2YyLTQxZmItYjUzYS1mN2UwOWQ0ZmU3N2UuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.kfwWkYRnR3C2a03BiWvOZw-1T8F_1SisnHxz1V2oThI', linkedin: '#', github: '#' },
  { name: 'Farzeen Shahid', desc: 'Built the few-shot model using Gemini API, developed the sentiment analysis API, conducted web scraping, and managed the database.', img: 'https://w7.pngwing.com/pngs/129/292/png-transparent-female-avatar-girl-face-woman-user-flat-classy-users-icon.png', linkedin: 'https://www.linkedin.com/in/farzeen-shahid-2233a2230', github: 'https://github.com/farzeenshahid' },
  { name: 'Syeda Afia Naeem', desc: 'Designed and developed an AI-powered chatbot for product recommendations and user queries.', img: 'https://www.svgrepo.com/show/382097/female-avatar-girl-face-woman-user-9.svg', linkedin: 'https://www.linkedin.com/in/afia-naeem-03058528b?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app', github: 'https://github.com/Afianaeem124' },
  { name: 'Urooj Khalid', desc: 'Developed the LSTM model, Designed Recommendation Frontend, built key frontend pages (Product Comparison, About Us, Home), and contributed to the backend.', img: 'https://as1.ftcdn.net/v2/jpg/01/16/24/44/1000_F_116244459_pywR1e0T3H7FPk3LTMjG6jsL3UchDpht.jpg', linkedin: 'https://www.linkedin.com/in/urooj-khalid-a40707285/', github: 'https://github.com/urooj-khalid5' },
  { name: 'Aliza Zahid', desc: 'Handled Backend, Integrated the chatbot to Frontend, developed the complete Product Recommendation page, and assisted with frontend tasks.', img: 'https://w7.pngwing.com/pngs/193/660/png-transparent-computer-icons-woman-avatar-avatar-girl-thumbnail.png', linkedin: 'https://www.linkedin.com/in/aliza-zahid-a90aa7246?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app', github: 'https://github.com/alizazahid11' },

];

const AboutPage = () => {
  return (
    <div className="about-container">
      <section className="about-section">
        <div className="container">
          {/* Our Mission Section */}
          <div className="text-container">
            <h2 className="center-heading">Our Mission</h2>
            <p className="center-text">
              At GlowBot, we believe that skincare should be personalized, data-driven, and easy to understand.
              Our AI-powered system helps users find the best skincare products based on real customer reviews, scientific insights, and their unique skin concerns.
            </p>
          </div>

          {/* What We Do Section */}
          <div className="text-container">
            <h2 className="center-heading">What GlowBot Do</h2>
            <ul className="feature-list">
              <li> Personalized Product Recommendations – Find the best products based on your skin type, concerns, and preferences.</li>
              <li> Sentiment-Based Insights – Understand what people are saying about a product before you buy.</li>
              <li> Product Comparison Tool – Compare ingredients, prices, and user satisfaction scores for better decision-making.</li>
              <li> AI-Powered Chatbot – Get instant skincare advice and recommendations.</li>
            </ul>
          </div>
        </div>
      </section>
      <section className="meet-our-team">
        <h2>Meet Our Team</h2>
        <div className="team-cards">
          {/* First row: 3 members */}
          {teamMembers.slice(0, 3).map((member, index) => (
            <div key={index} className="team-card">
              <img src={member.img} alt={member.name} />
              <h3>{member.name}</h3>
              <p className="seat">{member.seat}</p>
              <p>{member.desc}</p>
              <div className="socials">
                <a href={member.linkedin} target="_blank" rel="noopener noreferrer"><FaLinkedin /></a>
                <a href={member.github} target="_blank" rel="noopener noreferrer"><FaGithub /></a>
              </div>
            </div>
          ))}
        </div>

        {/* Second row: Centered 2 members */}
        <div className="team-cards second-row">
          {teamMembers.slice(3, 5).map((member, index) => (
            <div key={index} className="team-card">
              <img src={member.img} alt={member.name} />
              <h3>{member.name}</h3>
              <p className="seat">{member.seat}</p>
              <p>{member.desc}</p>
              <div className="socials">
                <a href={member.linkedin} target="_blank" rel="noopener noreferrer"><FaLinkedin /></a>
                <a href={member.github} target="_blank" rel="noopener noreferrer"><FaGithub /></a>
              </div>
            </div>
          ))}
        </div>
      </section>

      <style jsx>{`
        .about-container {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
        }

/* Heading style for sections */
.center-heading {
  font-size: 32px;
  color: black; 
  margin-bottom: 20px;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;

}
/* Text content in paragraphs */
.center-text {
  font-size: 20px;
  line-height: 1.4;
  max-width: 900px;
  margin-bottom: 20px;
    color: gray; 
            font-weight: bold; /* Added bold */
              font-family: "Times New Roman", Times, serif;

  margin-left: 30px;

}
/* Styling for the feature list with checkmarks */
.feature-list {
  list-style-type: none;
  padding: 0;
  font-size: 18px;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto 20px;
      color: gray; 

}
.feature-list li {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: bold;
                font-family: "Times New Roman", Times, serif;

}
.feature-list li::before {
  content: "✔ "; 
  color: black; 
  font-size: 20px;
}

.text-container {
  margin-bottom: 20px; /* Space between sections */
  max-width: 100%;
  width: 100%;
}
         h3 {
          color: black;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;

        }
        .meet-our-team {
          margin-top: 5px;
          text-align: center;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
        }

        h2 {
          margin-bottom: 30px;
          color:black;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;

        }

        .team-cards {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 100px;
          justify-content: center;
          margin-left: 30px;
        }

        .second-row {
          display: flex;
          justify-content: center;
          gap: 90px;
          margin-top: 60px;
        }

        .team-card {
          background-color: #ffffff;
          padding: 20px;
          text-align: center;
          border-radius: 15px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease;
          width: 250px;
          cursor:pointer;
        }

        .team-card:hover {
          transform: translateY(-10px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    
        }
          .team-card p {
  font-size: 12px;  /* Adjust the font size as needed */
  line-height: 1.4;  /* Adjust line spacing for readability */
}


        .team-card img {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          margin-bottom: 10px;
        }
        .socials {
          margin-top: 10px;
        }

        .socials a {
          margin: 0 10px;
          color: black;
          font-size: 1.5rem;
        }
          .socials a:hover{
          color:blue;
          }
      `}</style>
    </div>
  );
};

export default AboutPage;