# Docker Project

## Overview
This project is a Dockerized application that demonstrates how to set up and run a Python application using Docker.

## Project Structure
- **Dockerfile**: Contains instructions to build the Docker image.
- **docker-compose.yml**: Defines services, networks, and volumes for the application.
- **.dockerignore**: Lists files and directories to ignore when building the Docker image.
- **src/main.py**: The main entry point of the application.
- **requirements.txt**: Lists Python packages required for the project.
- **environment.yml**: Defines the conda environment for the project.

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Build the Docker Image
To build the Docker image, run the following command in the project directory:

```bash
docker build -t my-docker-project .
```

### Run the Application
To run the application using Docker Compose, use the following command:

```bash
docker-compose up
```

### Accessing the Application
Once the application is running, you can access it at `http://localhost:8000`.

## License
This project is licensed under the MIT License.