# Java Metrics Test Service

A Spring Boot service designed for testing Application Performance Monitoring (APM) tools and metrics collection with various endpoints and load testing capabilities.

## Endpoints

The service provides the following endpoints for testing different scenarios:

### 1. Health Check
- **URL**: `GET /health`
- **Description**: Returns the health status of the service
- **Response**: JSON object with status, timestamp, and service name

### 2. Sleep Endpoint
- **URL**: `GET /sleep/{sec}`
- **Description**: Sleeps for the specified number of seconds (useful for testing slow request scenarios)
- **Parameters**: 
  - `sec` (path parameter): Number of seconds to sleep (supports decimal values)
- **Response**: JSON object with sleep details and actual duration

### 3. Test Endpoints
- **URL**: `GET /test1`
- **Description**: Fast response endpoint for testing high-throughput scenarios
- **Response**: JSON object with instant completion message

- **URL**: `GET /test2`
- **Description**: Another fast response endpoint for load balancing tests
- **Response**: JSON object with instant completion message

### 4. Failure Testing Endpoints
- **URL**: `GET /fail-request`
- **Description**: Always returns a random 4xx HTTP error status (400-429)
- **Response**: JSON object with error message and random status code

- **URL**: `GET /raise-exception`
- **Description**: Always throws a RuntimeException for testing error handling
- **Response**: 500 Internal Server Error with exception details

## Load Testing

The repository includes a Python-based load testing script (`request-sender.py`) that can generate realistic traffic patterns for testing APM tools:

```bash
# Install dependencies
pip install httpx rich

# Run the load test (make sure the service is running first)
python request-sender.py
```

The load tester:
- Sends asynchronous requests to all endpoints
- Provides real-time progress monitoring with Rich UI
- Generates detailed logs including request counts per endpoint
- Supports configurable batch sizes and timing
- Tests various scenarios: fast responses, slow requests, failures, and exceptions

## Request Sender Script Details

The `request-sender.py` script is a sophisticated asynchronous load testing tool designed to generate realistic traffic patterns for APM testing:

### Key Features

**Asynchronous Architecture**
- Uses `asyncio` and `httpx` for high-performance concurrent requests
- Supports thousands of simultaneous connections without blocking
- Efficient resource utilization with async/await patterns

**Real-time Monitoring**
- Beautiful progress bar with Rich library showing live statistics
- Real-time updates of request counts per endpoint
- Elapsed time tracking and estimated completion time
- Console clearing for clean, updated displays

**Intelligent Traffic Generation**
- **Random batch sizes** (0-15 requests per batch) to simulate realistic load patterns
- **Mixed HTTP methods** (GET/POST) with weighted randomization (80% GET, 20% POST)
- **Variable timing** for sleep endpoint (0.0-1.0 seconds) to test slow requests
- **Background error generators** that continuously send failure and exception requests

**Comprehensive Logging**
- Detailed console logging with configurable log levels
- Persistent file logging to `request_count.log` with timestamps
- Per-endpoint request tracking and failure rates
- Session summaries with start/end times and total counts

### Traffic Patterns

The script generates several types of traffic simultaneously:

1. **Batch Traffic** (Main load):
   - Random batches of `/sleep/{time}` requests with 0-1 second delays
   - Random batches of `/test1` requests for fast response testing
   - Random batches of `/test2` requests for load balancing scenarios

2. **Background Error Traffic**:
   - Continuous `/fail-request` calls (every 5-10 seconds)
   - Continuous `/raise-exception` calls (every 5-10 seconds)
   - Simulates real-world error scenarios and exception handling

### Configuration

**Default Settings**:
- **Runtime**: 500 seconds (configurable via `TIME` variable)
- **Batch interval**: 0.1 seconds between batch sends
- **Timeout**: 1.0 second per request
- **Error frequency**: 5-10 second intervals for failure endpoints

**Customization Options**:
```python
# In the script, you can modify:
TIME = 500                    # Total runtime in seconds
timeout=Timeout(1.0)          # Request timeout
sleep_time = randint(5, 10)   # Error request frequency
LOG_LEVEL = "CRITICAL"        # Logging verbosity
```

### Output and Metrics

**Real-time Display**:
```
Total Batch: 125
Total Requests: 2,847
Failed Requests: 23
Endpoint Sleep: 1,203
Endpoint Test1: 856
Endpoint Test2: 742
Endpoint Fail: 23
Endpoint Exception: 23
```

**Log File Format** (`request_count.log`):
```
======================================================
# Log Time: 2025-08-07 12:26:37
Start Time: 2025-08-07 12:26:31
End Time: 2025-08-07 12:26:37
Elapsed Time: 0:00:05
Total Batches: 7
Total Requests: 130
Failed Requests: 0
Endpoint Sleep Requests: 36
Endpoint Test1 Requests: 56
Endpoint Test2 Requests: 36
Endpoint Fail Requests: 1
Endpoint Exception Requests: 1
```

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

# Fast test endpoints
curl http://localhost:5050/test1
curl http://localhost:5050/test2

# Test failure scenarios
curl http://localhost:5050/fail-request
curl http://localhost:5050/raise-exception
```

## APM Agent Support

The project includes APM agents for testing different monitoring solutions:

- **New Relic Agent**: `newrelic/` directory contains the Java agent and configuration
- **Elastic APM Agent**: `elastic-apm-agent.jar` for Elasticsearch APM
- **Atatus Agent**: `atatus-java-agent.jar` for Atatus monitoring

Configure the desired agent in the `Dockerfile` or via environment variables to test different APM solutions.

## Service Details

- **Base Package**: `com.mt`
- **Port**: 5050
- **Java Version**: 21
- **Spring Boot Version**: 3.1.2
- **Docker**: Multi-stage build optimized for production

## Project Structure

```
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # This file
├── request-sender.py           # Python load testing script
├── request_count.log           # Load test results log
└── metrics-test/               # Spring Boot application
    ├── Dockerfile
    ├── pom.xml
    ├── atatus-java-agent.jar   # Atatus APM agent
    ├── elastic-apm-agent.jar   # Elastic APM agent
    ├── newrelic/               # New Relic agent and config
    └── src/main/java/com/mt/   # Application source code
```

## Additional Features

- Spring Boot Actuator for monitoring endpoints
- Docker health checks
- Comprehensive error handling
- Detailed response metadata including timestamps and durations
- Support for multiple APM agents (New Relic, Elastic APM, Atatus)
- Realistic load testing scenarios with Python script
- Configurable failure rates and response times for testing edge cases