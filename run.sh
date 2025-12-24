#!/bin/bash

# Start the backend in the background
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start the frontend
python3 -m streamlit run ui/app.py --server.port 8501

# Kill backend when frontend stops
trap "kill 0" EXIT
