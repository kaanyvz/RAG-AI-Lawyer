FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the entire backend directory into the container
COPY backend /app/backend

# Change directory to backend
WORKDIR /app/backend

# Copy the requirements file
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "routes.routes:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
