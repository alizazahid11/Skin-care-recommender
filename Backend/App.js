const express = require('express');
const mongoose = require('mongoose');
const axios = require('axios');

const app = express();
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

// MongoDB URI and connection
const mongoURI = 'mongodb://skincare14:skincarerecommender@clusterskincare-shard-00-00.6sapl.mongodb.net:27017,clusterskincare-shard-00-01.6sapl.mongodb.net:27017,clusterskincare-shard-00-02.6sapl.mongodb.net:27017/final_database?replicaSet=atlas-1280kh-shard-0&ssl=true&authSource=admin';
mongoose.connect(mongoURI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.log('Failed to connect to MongoDB', err));

// Define the Product schema
const productSchema = new mongoose.Schema({
  Brand: String,
  "Product Name": String,
  price_in_pkr: Number,
  "Skin Type": String,
  Category: String,
  Benefit: String,
  Ingredients: String,
  URL: String,
});

const Product = mongoose.model('product', productSchema);

const reviewSchema = new mongoose.Schema({
  "Product Name": String,
  "ReviewText": String,
  Rating: Number,
  Sentiment: String,  
  Confidence_score: Number,
  product_id: { type: mongoose.Schema.Types.ObjectId, ref: 'product' }
});

const Review = mongoose.model('review', reviewSchema);


// API endpoint for fetching products based on filters
app.post('/api/products', async (req, res) => {
  try {
    const { skinType, category, brand } = req.body;

    // Build the filter query
    let query = { "Skin Type": skinType, Category: category };
    if (brand && brand !== 'All') {  
      query.Brand = brand;
    }

    // Query the database for products
    const products = await Product.find(query);

    // For each product, calculate the sentiment distribution and include the benefits and price
    const productsWithSentiment = await Promise.all(products.map(async (product) => {
      // Fetch the reviews associated with the product
      const reviews = await Review.find({ "Product Name": product["Product Name"] });

      // Calculate sentiment counts and confidence score
      const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
      let totalConfidence = 0;
      let totalReviews = reviews.length;

      reviews.forEach((review) => {
        sentimentCounts[review.Sentiment] += 1;
        totalConfidence += review.Confidence_score;
      });

      // Calculate the sentiment percentages
      const sentimentPercentages = {
        positive: (sentimentCounts.positive / totalReviews) * 100,
        negative: (sentimentCounts.negative / totalReviews) * 100,
        neutral: (sentimentCounts.neutral / totalReviews) * 100
      };

      // Calculate the average confidence score
      const averageConfidence = totalReviews > 0 ? totalConfidence / totalReviews : 0;

      // If no reviews or no sentiment available, set sentiment and confidence to "None"
      const sentiment = totalReviews === 0 || (sentimentCounts.positive === 0 && sentimentCounts.negative === 0 && sentimentCounts.neutral === 0)
        ? "None"
        : `${sentimentPercentages.positive.toFixed(2)}% positive (Confidence: ${averageConfidence.toFixed(2)}%)`;

      // Add the product name, benefits, sentiment, and price_in_pkr
      return {
        productName: product["Product Name"],
        benefits: product.Benefit,
        sentiment: sentiment,
        price: product.price_in_pkr  // Use the correct field name: price_in_pkr
      };
    }));

    res.json(productsWithSentiment);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});



// API endpoint for Rasa integration
app.post('/api/chat', async (req, res) => {
  const { message, sender } = req.body;

  try {
    // Send the message to the Rasa server
    const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
      sender, // Unique sender ID
      message, // User's message
    });

    // Return the Rasa response
    res.status(200).json(response.data);
  } catch (error) {
    console.error('Error communicating with Rasa:', error.message);
    res.status(500).json({ message: 'Error communicating with Rasa' });
  }
});

// Start the server
const PORT = 5009;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});