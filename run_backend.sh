#!/bin/bash
# Install dependencies and run backend

# Try using Python from Registry or direct path
PYTHON_PATH=$(python3 -c "import sys; print(sys.executable)" 2>/dev/null || echo "python")

echo "Using Python: $PYTHON_PATH"

# Install requirements
"$PYTHON_PATH" -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py --quiet 2>/dev/null

# Run backend
cd "$(dirname "$0")"
"$PYTHON_PATH" src/app/main.py
