#!/bin/bash

# java -javaagent:/usr/local/atatus-java-agent.jar \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5050

java -javaagent:/usr/local/atatus-java-agent.jar \
     -javaagent:/usr/local/newrelic/newrelic.jar \
      -jar target/metrics-test-1.0.0.jar \
     --server.port=5051 &

java -javaagent:/usr/local/atatus-java-agent.jar \
     -javaagent:/usr/local/newrelic/newrelic.jar \
      -jar target/metrics-test-1.0.0.jar \
     --server.port=5052 &

java -javaagent:/usr/local/atatus-java-agent.jar \
     -javaagent:/usr/local/newrelic/newrelic.jar \
      -jar target/metrics-test-1.0.0.jar \
     --server.port=5053 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-4" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5054 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-5" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5055 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-6" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5056 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-7" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5057 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-8" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5058 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-9" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5059 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-10" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5060 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-11" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5061 &

# java -javaagent:/usr/local/atatus-java-agent.jar \
#      -javaagent:/usr/local/newrelic/newrelic.jar \
#      -Datatus.hostname="darkglance-12" \
#       -jar target/metrics-test-1.0.0.jar \
#      --server.port=5062 &

wait
