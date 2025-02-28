FROM node:14.17.0 AS build-node

WORKDIR /app/frontend

# Copy the frontend app files into the container
COPY frontend/package*.json ./
COPY frontend/ .

RUN npm install
RUN npm run build src


FROM python:3.8-slim-buster

# Copy app.py, the user dir, and the requirements file into the container at /app/backend
COPY backend /app/backend/
# Copy the frontend build directory from build-node, the first stage
COPY --from=build-node /app/frontend/build /app/backend/build

WORKDIR /app/backend

# Install ffmpeg and portaudio19-dev so that we can use whisper
RUN apt-get update && apt-get install -y portaudio19-dev ffmpeg
# Install any needed packages specified in requirements.txt
RUN apt-get install -y git gcc
RUN pip install --trusted-host pypi.python.org --trusted-host github.com -r requirements.txt

EXPOSE 8000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--port=8000", "--host=0.0.0.0"] 

# user uses premade prompts file:
# user can retrieve dataset from output dir
# docker run -p 8000:8000 -v /Users/lee/projects/echo-keeper/output:/app/backend/user/projects echokeeper

# user provides their own prompts dir and prompts file:
# prompts go in /output/prompts/prompts.json
# user can retrieve dataset from output dir
# docker run -p 8000:8000 -v /Users/lee/projects/echo-keeper/output:/app/backend/user echokeeper