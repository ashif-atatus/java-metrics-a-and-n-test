# Java Metrics Test Service

A simple Spring Boot service for testing metrics and performance monitoring with Docker support.

## Endpoints

The service provides the following endpoints:

### 1. Health Check
- **URL**: `GET /health`
- **Description**: Returns the health status of the service
- **Response**: JSON object with status and timestamp

### 2. Sleep Endpoint
- **URL**: `GET /sleep/{sec}`
- **Description**: Sleeps for the specified number of seconds
- **Parameters**: 
  - `sec` (path parameter): Number of seconds to sleep
- **Response**: JSON object with sleep details and actual duration

### 3. Hash Computation Endpoint
- **URL**: `GET /hash/{iterations}`
- **Description**: Performs CPU-intensive hash computations using SHA-256
- **Parameters**: 
  - `iterations` (path parameter): Number of hash calculations to perform
- **Response**: JSON object with computation details and duration

## Running the Service

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

### Option 2: Using Maven

```bash
# Navigate to the metrics-test directory
cd metrics-test

# Build and run the service
./mvnw spring-boot:run
```

### Option 3: Using Docker directly

```bash
# Build the Docker image
cd metrics-test
docker build -t metrics-test .

# Run the container
docker run -p 5050:5050 metrics-test
```

## Example Usage

Once the service is running (on port 5050), you can test the endpoints:

```bash
# Health check
curl http://localhost:5050/health

# Sleep for 5 seconds
curl http://localhost:5050/sleep/5

# Perform 1000 hash computations
curl http://localhost:5050/hash/1000
```

## Service Details

- **Base Package**: `com.mt`
- **Port**: 5050
- **Java Version**: 21
- **Spring Boot Version**: 3.1.2
- **Docker**: Multi-stage build optimized for production

## Additional Features

- Spring Boot Actuator for monitoring endpoints
- Docker health checks
- Comprehensive error handling
- Detailed response metadata including timestamps and durations
- CPU-intensive hash computation endpoint using SHA-256 algorithm