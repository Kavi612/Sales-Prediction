from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

# Load the trained model
model = joblib.load("sales_prediction_model.pkl")  # Ensure correct model path

# Define expected product names from your dataset
product_lines = ["Electronic accessories", "Fashion accessories", "Food and beverages", 
                 "Health and beauty", "Home and lifestyle", "Sports and travel"]

# Encode product names into numerical values
label_encoder = LabelEncoder()
label_encoder.fit(product_lines)

@app.route('/')
def home():
    return render_template("index.html")  

@app.route('/products', methods=['GET'])
def get_products():
    """Returns the list of available products for dropdown selection."""
    return jsonify({'products': product_lines})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging log

        if not data:
            return jsonify({'error': 'No data received. Make sure you are sending JSON.'})

        # Validate and extract input values
        product_name = data.get("product")
        star_rating = data.get("starRating")
        unit_price = data.get("unitPrice")
        quantity = data.get("quantity")

        print(f"Extracted values -> Product: {product_name}, Star Rating: {star_rating}, Unit Price: {unit_price}, Quantity: {quantity}")

        if product_name is None or star_rating is None or unit_price is None or quantity is None:
            return jsonify({'error': 'Missing required input values', 'received_data': data})

        star_rating = int(star_rating)  # Review as stars (1-5)
        unit_price = float(unit_price)  # Ensure correct type conversion
        quantity = int(quantity)  

        # Convert product name to numerical encoding
        if product_name in product_lines:
            product_encoded = label_encoder.transform([product_name])[0]
        else:
            return jsonify({'error': 'Invalid product name'})

        # Prepare data in DataFrame format with correct feature order
        input_data = pd.DataFrame([[product_encoded, star_rating, unit_price, quantity]],
                                  columns=['Product', 'Review', 'Unit price', 'Quantity'])
        
        # Check if model supports these feature names
        model_feature_names = model.feature_names_in_  # Get trained feature names
        input_data = input_data[model_feature_names]  # Match order & remove missing columns
        
        # Predict sales
        prediction = model.predict(input_data)
        
        return jsonify({'predicted_sales': float(prediction[0])})  
    
    except Exception as e:
        return jsonify({'error': str(e)})  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)