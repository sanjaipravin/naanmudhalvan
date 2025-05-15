# AI Quality Control Dashboard

A Flask-based dashboard for monitoring AI model performance and data quality metrics.

## Features

- Real-time monitoring of model performance metrics (accuracy, precision, recall, F1 score)
- Data quality tracking (completeness, accuracy, consistency)
- Interactive charts using Plotly.js
- Responsive design with Bootstrap
- SQLite database for storing metrics
- RESTful API endpoints for data submission and retrieval

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

### Model Metrics

- GET `/api/model-metrics`: Retrieve recent model metrics
- POST `/api/add-model-metrics`: Add new model metrics
  ```json
  {
    "model_name": "model_v1",
    "accuracy": 0.95,
    "precision": 0.92,
    "recall": 0.94,
    "f1_score": 0.93
  }
  ```

### Data Quality

- GET `/api/data-quality`: Retrieve recent data quality metrics
- POST `/api/add-data-quality`: Add new data quality metrics
  ```json
  {
    "dataset_name": "training_data",
    "completeness": 0.98,
    "accuracy": 0.95,
    "consistency": 0.92
  }
  ```

## Directory Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
└── templates/         # HTML templates
    └── index.html     # Dashboard template
```

## Technologies Used

- Flask
- SQLAlchemy
- Plotly.js
- Bootstrap
- SQLite 