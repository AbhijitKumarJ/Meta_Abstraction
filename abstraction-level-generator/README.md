# Abstraction Level Generator

This project implements a system for generating and visualizing abstraction levels for given questions. It consists of a FastAPI backend for processing questions and generating abstractions, and a React frontend for user interaction and visualization.

## Project Structure

```
abstraction-level-generator/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── api.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── styles.css
│   ├── package.json
│   └── README.md
│
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the `backend` directory:
   ```
   cd abstraction-level-generator/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS and Linux: `source venv/bin/activate`

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up your OpenAI API key as an environment variable:
   - On Windows: `set OPENAI_API_KEY=your_api_key_here`
   - On macOS and Linux: `export OPENAI_API_KEY=your_api_key_here`

6. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```
   cd abstraction-level-generator/frontend
   ```

2. Install the required npm packages:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```

## Usage

1. Open your web browser and go to `http://localhost:3000`
2. Enter a question in the text area and click "Generate Abstractions"
3. View the generated abstraction levels and their visualization

## Project Components

- `backend/main.py`: Main FastAPI application
- `backend/database.py`: Database connection and operations
- `backend/models.py`: Pydantic models for request/response handling
- `backend/api.py`: API route handlers
- `frontend/src/App.js`: Main React component
- `frontend/src/index.js`: React entry point
- `frontend/src/styles.css`: CSS styles for the application

## Dependencies

- Backend: FastAPI, SQLite, aiohttp, uvicorn
- Frontend: React, axios, react-chartjs-2, Chart.js

