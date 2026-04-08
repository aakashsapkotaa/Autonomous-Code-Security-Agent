#!/bin/bash
# Start Celery worker

cd backend
celery -A celery_worker worker --loglevel=info --concurrency=4
