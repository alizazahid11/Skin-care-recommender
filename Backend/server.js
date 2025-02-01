const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

// Initialize the app
const app = express();
const port = 5004;

// Middleware
app.use(express.json());
const corsOptions = {
    origin: 'http://localhost:3000', // Replace with your frontend's URL
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type'],
};
app.use(cors(corsOptions));

// MongoDB connection URI
const dbURI = "mongodb://localhost:27017/SkinProducts";

// Connect to MongoDB
mongoose.connect(dbURI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log("MongoDB Connected"))
    .catch(err => console.error("MongoDB Connection Error: ", err));

// Define the Product schema
const productSchema = new mongoose.Schema({
    Brand: String,
    'Product Name': String,
    'Skin Type': String,
    Category: String,
    Ingredients: String,
});

// Create the Product model
const Product = mongoose.model('products', productSchema);

const getRecommendations = async (req, res) => {
    try {
        const { skinType, category, brand, ingredients } = req.body;

        const query = {};

        // Dynamically build the query based on the filters
        if (skinType) {
            query["Skin Type"] = { $regex: skinType, $options: "i" };
        }
        if (category) {
            query["Category"] = { $regex: category, $options: "i" };
        }
        if (brand) {
            query["Brand"] = { $regex: brand, $options: "i" };
        }
        if (ingredients) {
            query["Ingredients"] = { $regex: ingredients, $options: "i" };
        }

        // Add a search to the 'Product Name' field only if necessary
        const orConditions = [];
        if (skinType) {
            orConditions.push({ "Product Name": { $regex: skinType, $options: "i" } });
        }
        if (category) {
            orConditions.push({ "Product Name": { $regex: category, $options: "i" } });
        }
        if (brand) {
            orConditions.push({ "Product Name": { $regex: brand, $options: "i" } });
        }
        if (ingredients) {
            orConditions.push({ "Product Name": { $regex: ingredients, $options: "i" } });
        }

        // Only add the $or condition if there are any conditions to search for 'Product Name'
        if (orConditions.length > 0) {
            query["$or"] = orConditions;
        }

        console.log("Constructed query:", query); // Log the query for debugging

        // Search the products in the database and select only the 'Product Name' field
        const products = await Product.find(query, { "Product Name": 1, "_id": 0 });

        console.log("Found products:", products); // Log the results for debugging
      
        res.json(products); // Return the results to the frontend
        console.log("Constructed query:", query); // This will show the query being sent to MongoDB
        console.log(req.body); // Ensure the body contains correct filters
        

    } catch (error) {
        console.error("Error:", error);
        res.status(500).send("Server Error");
    }
};


// Define route to get product recommendations
app.post('/get-recommendations', getRecommendations);

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});