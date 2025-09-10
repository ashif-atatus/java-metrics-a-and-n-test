  # Use OpenJDK 21 as base image
  FROM openjdk:21-jdk-slim

  # Install curl for health checks
  RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

  # Set working directory
  WORKDIR /app

  # Copy Maven wrapper and pom.xml first for better caching
  COPY mvnw .
  COPY .mvn .mvn
  COPY pom.xml .

  # Make mvnw executable
  RUN chmod +x mvnw

  # Copy source code
  COPY src src

  # Build the application (download dependencies and build in one step)
  RUN ./mvnw clean package -DskipTests

  RUN mkdir -p /usr/local/newrelic
  ADD ./newrelic/newrelic.jar /usr/local/newrelic/newrelic.jar
  ADD ./newrelic/newrelic.yml /usr/local/newrelic/newrelic.yml
  # ADD ./atatus-java-agent.jar /usr/local/atatus-java-agent.jar
  # ADD ./elastic-apm-agent.jar /usr/local/elastic-apm-agent.jar

  ADD ./atatus-java-agent.jar /usr/local/atatus-java-agent.jar
  ADD entrypoint.sh entrypoint.sh

  RUN chmod +x entrypoint.sh

  # Expose port
  EXPOSE 5050
  EXPOSE 5051

  # Run the application
  # CMD ["java", "-jar", "target/metrics-test-1.0.0.jar"]
  ENTRYPOINT [ \
    "java", \
    "-javaagent:/usr/local/newrelic/newrelic.jar", \
    "-javaagent:/usr/local/atatus-java-agent.jar", \
    # "-javaagent:/usr/local/elastic-apm-agent.jar", \
    "-jar", \
    "target/metrics-test-1.0.0.jar" \
  ]
  # ENTRYPOINT [ "./entrypoint.sh" ]

