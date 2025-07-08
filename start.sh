#!/bin/bash
echo "🚀 Starting Lexi AI Agent server..."
uvicorn main:app --host 0.0.0.0 --port 8000
