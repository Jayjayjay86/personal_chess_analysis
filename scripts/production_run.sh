#!/bin/bash

# Chess Analysis App - Production Runner

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
python app.py --prod &

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm run start-prod &

echo ""
echo "Chess Analysis App is running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
wait