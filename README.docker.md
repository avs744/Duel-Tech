# DuelTech Docker Deployment Guide

This guide explains how to deploy the DuelTech application using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system

## Quick Start

1. Navigate to the project directory:
   ```
   cd path/to/project
   ```

2. Make sure your `.env` file is properly configured:
   ```
   # Example .env file
   DATABASE_URL=sqlite:///dueltech.db
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_ENV=production
   FLASK_DEBUG=0
   ```

3. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

4. Access the application at [http://localhost:5000](http://localhost:5000)

## Docker Commands

- **Start the application**:
  ```
  docker-compose up -d
  ```

- **View logs**:
  ```
  docker-compose logs -f
  ```

- **Stop the application**:
  ```
  docker-compose down
  ```

- **Rebuild the application after changes**:
  ```
  docker-compose up -d --build
  ```

## Configuration

The application uses environment variables for configuration. These can be set in the `.env` file or directly in the `docker-compose.yml` file.

## Database

By default, the application uses SQLite. The database file is stored in a Docker volume to persist data between container restarts.

## Troubleshooting

- If you encounter permission issues with the database file, you may need to adjust the permissions:
  ```
  chmod 666 dueltech.db
  ```

- If the application fails to start, check the logs:
  ```
  docker-compose logs -f
  ```
