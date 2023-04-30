# Use an official Node.js runtime as a parent image
FROM node:14.17.0 AS build-node

# Set the working directory to /app
WORKDIR /app/frontend

# Copy the frontend app files into the container
COPY frontend/package*.json ./
COPY frontend/ .

# Install dependencies for the frontend app
RUN npm install

# Build the frontend app
RUN npm run build


# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app/backend

# Copy the requirements file into the container at /app/backend
COPY backend/requirements.txt .

# Copy the frontend build directory from the first stage
COPY --from=build-node /app/frontend/build /app/backend/build

# Install ffmpeg and portaudio19-dev so that we can use whisper
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg

# Install any needed packages specified in requirements.txt
RUN apt-get install -y git gcc
RUN pip install --trusted-host pypi.python.org --trusted-host github.com -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose the port that the app will run on
EXPOSE 8000

# Set environment variables
ENV FLASK_APP=app.py

# Run the command to start the server
CMD ["flask", "run", "--port=8000", "--host=0.0.0.0"] 

# docker run -p 8000:8000 -v /Users/lee/projects/echo-keeper/output:/app/backend/projects echokeeper