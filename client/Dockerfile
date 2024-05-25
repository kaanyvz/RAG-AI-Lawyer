# Use a base image with Node.js
FROM node:14

# Set the working directory in the container
WORKDIR /app/client

# Copy the entire client directory into the container
COPY client /app/client

# Change directory to client
WORKDIR /app/client

# Install http-server globally
RUN npm install -g http-server

# Expose port for HTTP server
EXPOSE 8080

# Command to run the HTTP server
CMD ["http-server", "--port", "8080"]
