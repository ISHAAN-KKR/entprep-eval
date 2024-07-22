from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import pandas as pd
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load MongoDB URI from environment variables
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("MONGO_URI is not set in the environment variables")

logging.debug(f"Connecting to MongoDB at URI: {mongo_uri}")
app.config["MONGO_URI"] = mongo_uri

try:
    mongo = PyMongo(app)
    logging.debug("Successfully connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise

# Define columns and selected columns
columns = [
    'Convenience', 'Essentials', 'Community', 'Strategic Partnerships', 'Brand Loyalty', 'Niche',
    'Accessibility', 'Loyalty Program', 'Discreet', 'Customer-Centric', 'Hybrid Retail', 'E-commerce',
    'Subscription Services', 'Data Analytics', 'Eco-friendly', 'Affordability', 'Partnerships',
    'Technology', 'Repair Services', 'Workshops', 'Discounts', 'Trends', 'Diverse Menu',
    'Delivery Services', 'Ambiance', 'Local Suppliers', 'Sustainability'
]

selected_columns = columns[:15]

def process_paragraph(paragraph):
    sentences = paragraph.split('.')
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    if len(sentences) != 10:
        raise ValueError("The paragraph must contain exactly 10 sentences.")

    df = pd.DataFrame(0, index=range(10), columns=selected_columns)

    for i, sentence in enumerate(sentences):
        for word in selected_columns:
            if word.lower() in sentence.lower():
                df.loc[i, word] = 1

    df['Sum'] = df[selected_columns].sum(axis=1)

    return df

def evaluate_skills(df):
    total_sum = df['Sum'].sum()

    if total_sum > 7:
        overall_evaluation = 'High Entrepreneurship Skills'
    elif 2 < total_sum <= 7:
        overall_evaluation = 'Average'
    else:
        overall_evaluation = 'Needs Improvement'

    return overall_evaluation

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    username = data['username']
    paragraph = data['paragraph']

    try:
        df = process_paragraph(paragraph)
        evaluation = evaluate_skills(df)

        # Store data in MongoDB
        mongo.db.Users.insert_one({
            'username': username,
            'paragraph': paragraph,
            'evaluation': evaluation
        })

        return jsonify({
            'message': 'Data successfully processed and stored',
            'evaluation': evaluation
        })

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    try:
        user_data = mongo.db.Users.find_one({'username': username})

        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        return render_template('user.html', user=user_data)

    except Exception as e:
        logging.error(f"Failed to fetch user data: {e}")
        return jsonify({'error': 'An error occurred while fetching user data'}), 500


