# **AI-Powered Skincare Recommendation System**

## **Table of Contents**
- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Setup and Installation](#setup-and-installation)
- [Usage Guide](#usage-guide)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Contributors](#contributors)

---

## **Project Overview**
This AI-powered skincare recommendation system helps users find the best skincare products based on **sentiment analysis of product reviews**, ingredient analysis, and **personalized recommendations**. It utilizes **machine learning models** and a **chatbot** to assist users in making informed skincare choices.

### **Motivation**
- Users struggle to find skincare products that suit their **skin type and concerns**.
- Online product reviews are often **unstructured and overwhelming**.
- There is a need for an AI-driven solution to analyze and summarize skincare product reviews effectively.

---

## **Features**
+ **Product Recommendation System** – Users can filter products based on **skin type, category, and brand**.
+ **Sentiment Analysis** – Extracts insights from user reviews, displaying overall sentiment percentages (**Positive, Neutral, Negative**).
+ **Chatbot Assistance** – AI chatbot recommends skincare products based on user queries.
+ **Product Comparison** – Users can compare **two skincare products** based on ingredients, price, suitability, and sentiment trends.
+ **User-Friendly Interface** – A clean and intuitive **web-based platform** for browsing skincare products.

---

## **Technology Stack**
### **Frontend:**
- React.js

### **Backend:**
- Node.js
- Express.js
- MongoDB Atlas

### **Machine Learning Models:**
- **Fine-tuned BERT Model** (Hugging Face) – Sentiment Analysis
- **LSTM Model** – Alternative model for sentiment classification
- **Gemini Pro API (Few-Shot Learning)** – Initially tested for classification

### **Chatbot:**
- **Rasa AI Chatbot** – Provides personalized product recommendations

### **APIs:**
- Custom-built **Sentiment Analysis API** for classifying skincare product reviews.
- Chatbot API for retrieving product information and recommendations.

---

## **System Architecture**
```
User → Frontend (React.js) → Backend (Node.js, Express.js) → Database (MongoDB Atlas) →
Sentiment Analysis API (BERT Model) → Chatbot (Rasa) → Recommendations & Comparisons
```
---

## **Setup and Installation**
### **Prerequisites**
- Node.js & npm installed
- MongoDB Atlas database set up
- Python & required ML libraries installed

### **Backend Setup**
```sh
cd backend
npm install
npm start
```

### **Frontend Setup**
```sh
cd frontend
npm install
npm start
```

### **ML Model Setup**
```sh
cd sentiment_model
pip install -r requirements.txt
python app.py
```

---

## **Usage Guide**
1. Open the **web application** in a browser.
2. Navigate to the **product recommendation page** and apply filters.
3. Use the **chatbot** to ask for personalized skincare suggestions.
4. Compare two products on the **comparison page**.
5. View product reviews along with sentiment scores.

---

## **API Endpoints**
### **Sentiment Analysis API**
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/analyze_reviews_with_no_sentiment` | Classifies a review as **positive, neutral, or negative** and returns a confidence score. |

### **Chatbot API**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/chat` | Sends a user query to the chatbot and returns recommended products. |

---

## **Database Schema**
### **1. Products Table**
| Field | Type | Description |
|--------|------|-------------|
| product_id | ObjectID | Unique identifier |
| Brand | String | Brand name |
| Product Name | String | Product name |
| price_in_pkr| String | Product Price
| Category | String | Product category |
| Skin Type | String | Suitable skin types |
| Benefit| String | Skin concerns addressed|
| Ingredients | String | List of ingredients |
| Product Rating| Double | Overall product rating
### **2. Reviews Table**
| Field | Type | Description |
|--------|------|-------------|
| _id | ObjectID | Unique identifier |
| product_id | ObjectID | References the product |
| ReviwText | String | Review text |
| Rating | Double | Star rating |
| Sentiment | String | Sentiment classification |
| Confidence_score | Double | Model confidence score |

---

## **Contributors**
- **Member 1:** Developed BERT model, Web Scraping, Assisted in LSTM model development.
- **Member 2:** Developed Few-Shot Learning with Gemini API, Web Scraping, Built Sentiment Analysis API, Set up Database.
- **Member 3:** Developed Chatbot.
- **Member 4:** Developed LSTM Model, Frontend (Product Comparison, Home, About Us, UI setup for Recommendation Page), Assisted in Backend.
- **Member 5:** Backend (Chatbot integration), Frontend (Product Recommendation Page Development).

---

✨ **Empowering Skincare Choices with AI!** ✨
