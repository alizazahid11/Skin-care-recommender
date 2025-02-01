import React, { useState } from 'react';
import './Recommendation.css';

const Recommendation = () => {
    const [skinType, setSkinType] = useState('');
    const [category, setCategory] = useState('');
    const [brand, setBrand] = useState('All');
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
 // Debugging: Monitor `products` state updates
 useEffect(() => {
    fetch('/api/products')
      .then((res) => res.json())
      .then((data) => setProducts(data)) // Make sure data structure is handled properly
      .catch((err) => console.error('Error fetching products:', err));
  }, []);
  
    const handleRecommendation = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    skinType,
                    category,
                    brand,
                }),
            });
    
            if (response.ok) {
                const data = await response.json();
                console.log("Fetched Products:", data); // Debugging Log
                setProducts(data);
            } else {
                console.error('Failed to fetch products');
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };
    

    return (
        <div className="Recommendation">
            <h1 className="app-title">Skin Product Recommendation</h1>

            <div className="form-container">
                <div className="form-group">
                    <label>Skin Type: </label>
                    <select onChange={(e) => setSkinType(e.target.value)} value={skinType}>
                        <option value="">Select Skin Type</option>
                        <option value="All">All</option>
                        <option value="All/dry">All/Dry</option>
                        <option value="Very Dry">Very Dry</option>
                        <option value="All/Aging">All/Aging</option>
                        <option value="All/Oily/Acne-prone">All/Oily/Acne-prone</option>
                        <option value="All/Dry/Sensitive">All/Dry/Sensitive</option>
                        <option value="All/Dry/Sensitive">All/Dry/Sensitive</option>
                        <option value="Oily">Oily</option>
                        <option value="Balanced/Oily">Balanced/Oily</option>
                        <option value="Oily/Acne-prone">Oily/Acne-prone</option>
                        <option value="Dry">Dry</option>
                        <option value="Balanced/Dry">Balanced/Dry</option>
                        <option value="Dry/Aging">Dry/Aging</option>
                        <option value="Dull/Aging">Dull/Aging</option>
                        <option value="Normal/Dry<">Normal/Dry</option>
                        <option value="All/Normal/Dry">All/Normal/Dry</option>
                        <option value="Normal/Oily">Normal/Oily</option>
                        <option value="Normal/Dry/Sensitive">Normal/Dry/Sensitive</option>
                        <option value="Combination">Combination</option>
                        <option value="Combination/Acne-prone">Combination/Acne-prone</option>
                        <option value="Oily/Combination">Oily/Combination</option>
                        <option value="Sensitive">Sensitive</option>
                        <option value="All/Sensitive">All/Sensitive</option>
                        <option value="Dry/Sensitive">Dry/Sensitive</option>
                        <option value="Pigmentation">Pigmentation</option>
                        <option value="Rough/Bumpy">Rough/Bumpy</option>
                        <option value="Inflammed/ALL">Inflammed/ALL</option>
                        <option value="Oily,Sun damaged">Oily,Sun damaged</option>
                        <option value="Damaged/DullRough/Dehydrated/Irritated">Damaged/DullRough/Dehydrated/Irritated</option>
                        <option value="Acne-prone/Inflammed/Irritated">Acne-prone/Inflammed/Irritated</option>
                        <option value="Dehydrated/Achne prone/Pigmented">Dehydrated/Achne prone/Pigmented</option>
                        <option value="Flared/Irriated skin">Flared/Irriated skin</option>
                        <option value="Dull/Uneven/Aging">Dull/Uneven/Aging</option>
                        <option value="Aging/Uneven">Aging/Uneven</option>
                        <option value="clogged/Oily/Acne prone">clogged/Oily/Acne prone</option>
                        <option value="Dull/Hyperpigmentation">Dull/Hyperpigmentation</option>
                        <option value="Acne prone/Blemish">Acne prone/Blemish</option>
                        <option value="Uneven/Dull/Tanned">Uneven/Dull/Tanned</option>
                        <option value="Dry/Itchy">Dry/Itchy</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Category: </label>
                    <select onChange={(e) => setCategory(e.target.value)} value={category}>
                        <option value="">Select Category</option>
                        <option value="Cleanser">Cleanser</option>
                        <option value="Moisturizer">Moisturizer</option>
                        <option value="Serum">Serum</option>
                        <option value="Eye Serum">Eye Serum</option>
                        <option value="Sunscreen">Sunscreen</option>
                        <option value="Eye Cream">Eye Cream</option>
                        <option value="Exfoliator">Exfoliator </option>
                        <option value="Makeup remover">Makeup remover </option>
                        <option value="Toner">Toner </option>
                        <option value="Patch">Patch </option>
                        <option value="Mask">Mask </option>
                        <option value="Micellar water">Micellar water </option>
                        <option value="Care set">Care set </option>
                        <option value="Wipes">Wipes </option>
                        <option value="Gel">Gel </option>
                        <option value="Lip Balm">Lip Balm </option>
                        <option value="Face Oil" >Face Oil </option>
                        <option value="Essential Oil" >Essential Oil </option>
                        <option value="Body Wash" >Body Wash </option>
                        <option value="Facial Cleanser" >Facial Cleanser </option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Brand: </label>
                    <select onChange={(e) => setBrand(e.target.value)} value={brand}>
                        <option value="All">All Brands</option>
                        <option value="CeraVe">CeraVe</option>
                        <option value="Neutrogena">Neutrogena</option>
                        <option value="The Ordinary">The Ordinary</option>
                        <option value="Cosrx">Cosrx</option>
                        <option value="The Body Shop">The Body Shop</option>
                        <option value="Skindeepintl">Skindeepintl</option>
                        <option value="The Inkey List">The Inkey List</option>
                        <option value="Conatural">Conatural</option>
                    </select>
                </div>

                <button className="search-button" onClick={handleRecommendation} disabled={loading}>
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </div>
            <div className="results-container">
    <h2>Recommended Products</h2>
    {products.length > 0 ? (
        <ul>
            {products.map((product, index) => (
                <li key={index}>
                    <h3>{product.productName}</h3>
                    <p>Positive: {product.sentimentPercentages?.positive ? product.sentimentPercentages.positive.toFixed(2) : '0'}%</p>
<p>Negative: {product.sentimentPercentages?.negative ? product.sentimentPercentages.negative.toFixed(2) : '0'}%</p>
<p>Neutral: {product.sentimentPercentages?.neutral ? product.sentimentPercentages.neutral.toFixed(2) : '0'}%</p>

                </li>
            ))}
        </ul>
    ) : (
        <p>No products found.</p>
    )}
</div>

        </div>
    );
};

export default Recommendation;