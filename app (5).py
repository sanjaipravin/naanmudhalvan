from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_quality.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class ModelMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DataQuality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(100), nullable=False)
    completeness = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    consistency = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/model-metrics')
def get_model_metrics():
    df = pd.read_csv('static/data/laptops.csv')
    
    # Generate quality metrics for each model
    metrics = []
    for _, row in df.iterrows():
        # Calculate metrics based on sales and defect rates
        accuracy = (100 - row['defect_rate']) / 100
        precision = max(0, min(1, 1 - (row['defect_rate'] / 100)))
        recall = max(0, min(1, row['sales_count'] / 1000))
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics.append({
            'model_name': f"{row['brand']} {row['model']}",
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Sort by accuracy descending
    metrics.sort(key=lambda x: x['accuracy'], reverse=True)
    return jsonify(metrics[:10])  # Return top 10 models

@app.route('/api/data-quality')
def get_data_quality():
    quality_metrics = DataQuality.query.order_by(DataQuality.timestamp.desc()).limit(10).all()
    return jsonify([{
        'dataset_name': q.dataset_name,
        'completeness': q.completeness,
        'accuracy': q.accuracy,
        'consistency': q.consistency,
        'timestamp': q.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for q in quality_metrics])

@app.route('/api/add-model-metrics', methods=['POST'])
def add_model_metrics():
    data = request.json
    new_metrics = ModelMetrics(
        model_name=data['model_name'],
        accuracy=data['accuracy'],
        precision=data['precision'],
        recall=data['recall'],
        f1_score=data['f1_score']
    )
    db.session.add(new_metrics)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/add-data-quality', methods=['POST'])
def add_data_quality():
    data = request.json
    new_quality = DataQuality(
        dataset_name=data['dataset_name'],
        completeness=data['completeness'],
        accuracy=data['accuracy'],
        consistency=data['consistency']
    )
    db.session.add(new_quality)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/laptop-data')
def get_laptop_data():
    df = pd.read_csv('static/data/laptops.csv')
    category = request.args.get('category', None)
    price_range = request.args.get('price_range', None)
    
    if category and category != 'All':
        df = df[df['category'] == category]
    
    if price_range:
        price_ranges = {
            'budget': (0, 700),
            'mid': (701, 1200),
            'premium': (1201, float('inf'))
        }
        if price_range in price_ranges:
            min_price, max_price = price_ranges[price_range]
            df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
    
    # Prepare data for different charts
    brand_sales = df.groupby('brand')['sales_count'].sum().to_dict()
    category_defects = df.groupby('category')['defect_rate'].mean().to_dict()
    price_distribution = df.groupby('category')['price'].mean().to_dict()
    
    return jsonify({
        'brandSales': brand_sales,
        'categoryDefects': category_defects,
        'priceDistribution': price_distribution,
        'rawData': df.to_dict('records')
    })

@app.route('/api/filters')
def get_filters():
    df = pd.read_csv('static/data/laptops.csv')
    return jsonify({
        'categories': sorted(df['category'].unique().tolist()),
        'brands': sorted(df['brand'].unique().tolist()),
        'priceRanges': ['budget', 'mid', 'premium']
    })

@app.route('/api/price-performance')
def get_price_performance():
    df = pd.read_csv('static/data/laptops.csv')
    
    # Calculate performance score based on specs
    df['performance_score'] = (
        df['ram'] / 32 * 0.3 +  # Normalize RAM and weight 30%
        df['storage'] / 1024 * 0.3 +  # Normalize storage and weight 30%
        (100 - df['defect_rate']) / 100 * 0.4  # Quality score weighted 40%
    ) * 100  # Convert to percentage
    
    return jsonify({
        'prices': df['price'].tolist(),
        'performance': df['performance_score'].tolist(),
        'models': [f"{row['brand']} {row['model']}" for _, row in df.iterrows()],
        'categories': df['category'].tolist()
    })

@app.route('/api/model-comparison')
def get_model_comparison():
    df = pd.read_csv('static/data/laptops.csv')
    
    # Select top 5 models by sales
    top_models = df.nlargest(5, 'sales_count')
    
    # Calculate normalized scores for each metric
    metrics = {
        'Quality': (100 - top_models['defect_rate']) / 100 * 10,  # Convert to 0-10 scale
        'Performance': top_models['ram'] / 32 * 10,  # RAM as performance indicator
        'Value': (2000 - top_models['price']) / 2000 * 10,  # Inverse price (higher is better)
        'Storage': top_models['storage'] / 1024 * 10,  # Storage score
        'Popularity': top_models['sales_count'] / 1200 * 10  # Sales score
    }
    
    return jsonify({
        'models': [f"{row['brand']} {row['model']}" for _, row in top_models.iterrows()],
        'metrics': list(metrics.keys()),
        'scores': [metrics[metric].tolist() for metric in metrics.keys()]
    })

if __name__ == '__main__':
    app.run(debug=True) 