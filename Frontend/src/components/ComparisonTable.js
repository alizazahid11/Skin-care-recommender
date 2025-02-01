import React, { useState } from 'react';
import '../styles/styles.css';
import { product } from '../data/data';

const ComparisonTable = () => {
    const [selectedProduct1, setSelectedProduct1] = useState(null);
    const [selectedProduct2, setSelectedProduct2] = useState(null);

    const renderStars = (rating) => {
        let stars = [];
        for (let i = 1; i <= 5; i++) {
            stars.push(
                <i
                    key={i}
                    className={i <= Math.floor(rating) ? 'fas fa-star' : 'far fa-star'}
                    style={{ color: i <= rating ? 'rgb(22, 20, 16)' : 'rgb(15, 14, 12)' }}
                ></i>
            );
        }
        if (rating % 1 !== 0) {
            stars.splice(
                Math.floor(rating),
                1,
                <i
                    key="half-star"
                    className="fas fa-star-half-alt"
                    style={{ color: 'rgb(39, 38, 37)' }}
                ></i>
            );
        }
        return stars;
    };

    const renderProductDetails = (product) => (
        <div className="product-details">
            <table className="table">
                <tbody>
                    <tr>
                        <th>Product Image</th>
                        <td>
                            <img
                                src={product.image || 'https://via.placeholder.com/200'}
                                alt="Product Image"
                                style={{ width: '200px', height: '200px', borderRadius: '50%', border: '3px solid black' }}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th>Brand Name</th>
                        <td>{product.Brand || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Price</th>
                        <td>{product.price_in_pkr || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Rating</th>
                        <td>{renderStars(product.Rating)}</td>
                    </tr>
                    <tr>
                        <th>Sentiment</th>
                        <td>{product.Sentiment || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Active Ingredients</th>
                        <td>{product['Active Ingredient'] || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Category</th>
                        <td>{product.Category || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Skin Type</th>
                        <td>{product['Skin Type'] || 'N/A'}</td>
                    </tr>
                    <tr>
                        <th>Benefits</th>
                        <td>{product.Benefits || 'N/A'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="container">
            <h1>Skincare Product Comparison</h1>
            <div className="dropdown-container">
                <div className="dropdown-section">
                    <label>Choose Product 1</label>
                    <select
                        onChange={(e) => setSelectedProduct1(product[e.target.value])}
                        className="form-control"
                    >
                        <option value="">-- Choose a product --</option>
                        {product.map((p, i) => (
                            <option key={i} value={i}>
                                {p.Name}
                            </option>
                        ))}
                    </select>
                    {selectedProduct1 && renderProductDetails(selectedProduct1)}
                </div>

                <div className="dropdown-section">
                    <label>Choose Product 2</label>
                    <select
                        onChange={(e) => setSelectedProduct2(product[e.target.value])}
                        className="form-control"
                    >
                        <option value="">-- Choose a product --</option>
                        {product.map((p, i) => (
                            <option key={i} value={i}>
                                {p.Name}
                            </option>
                        ))}
                    </select>
                    {selectedProduct2 && renderProductDetails(selectedProduct2)}
                </div>
            </div>
        </div>
    );
};

export default ComparisonTable;

