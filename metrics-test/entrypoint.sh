#!/bin/bash

java -javaagent:/usr/local/atatus-java-agent.jar \
      -jar target/metrics-test-1.0.0.jar \
     --server.port=5050

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5050

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5051 &

# wait