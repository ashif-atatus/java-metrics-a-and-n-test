package com.mt.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

@RestController
public class MetricsController {

    private static final Logger logger = LoggerFactory.getLogger(MetricsController.class);

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        logger.info("GET /health");
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", java.time.Instant.now().toString());
        response.put("service", "metrics-test");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/sleep/{sec}")
    public ResponseEntity<Map<String, Object>> sleep(@PathVariable double sec) {
        logger.info("GET /sleep/{}", sec);
        long startTime = System.currentTimeMillis();

        try {
            long millis = (long) (sec * 1000);
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Sleep interrupted");
            errorResponse.put("timestamp", java.time.Instant.now().toString());
            return ResponseEntity.internalServerError().body(errorResponse);
        }

        long endTime = System.currentTimeMillis();
        long actualDuration = endTime - startTime;

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Sleep completed");
        response.put("requestedSeconds", sec);
        response.put("actualDurationMs", actualDuration);
        response.put("timestamp", java.time.Instant.now().toString());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/fail-request")
    public ResponseEntity<Map<String, Object>> failRequest() {
        logger.info("GET /fail-request");
        Map<String, Object> response = new HashMap<>();
        response.put("error", "This endpoint always fails the request");
        response.put("timestamp", java.time.Instant.now().toString());
        int[] statusCodes = {400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 429};
        int randomStatus = statusCodes[ThreadLocalRandom.current().nextInt(statusCodes.length)];
        return ResponseEntity.status(randomStatus).body(response);
    }

    @GetMapping("/raise-exception")
    public ResponseEntity<Map<String, Object>> raiseException() {
        logger.info("GET /raise-exception");
        throw new RuntimeException("This endpoint always throws an exception");
    }

    @GetMapping("/instant")
    public ResponseEntity<Map<String, Object>> test1() {
        logger.info("GET /test1");
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Test1 completed instantly");
        response.put("requestedSeconds", 0.0);
        response.put("actualDurationMs", 0);
        response.put("timestamp", java.time.Instant.now().toString());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/stream")
    public ResponseEntity<org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody> streamTest(
            @RequestParam(name = "sizeMb", required = false, defaultValue = "10") int sizeMb,
            @RequestParam(name = "chunkKb", required = false, defaultValue = "64") int chunkKb,
            @RequestParam(name = "bytesPerSec", required = false, defaultValue = "0") long bytesPerSec
    ) {
        final long totalBytes = Math.max(1, sizeMb) * 1024L * 1024L;
        final int chunkBytes = Math.max(1, chunkKb) * 1024;
        final byte[] chunk = new byte[chunkBytes]; // zero-filled

        logger.info("GET /stream-test sizeMb={} chunkKb={} bytesPerSec={}", sizeMb, chunkKb, bytesPerSec);

        org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody stream = outputStream -> {
            long sent = 0;
            while (sent < totalBytes) {
                int toWrite = (int) Math.min(chunkBytes, totalBytes - sent);
                outputStream.write(chunk, 0, toWrite);
                outputStream.flush();
                sent += toWrite;

                if (bytesPerSec > 0) {
                    double secondsForChunk = (double) toWrite / (double) bytesPerSec;
                    long sleepMs = (long) Math.ceil(secondsForChunk * 1000.0);
                    if (sleepMs > 0) Thread.sleep(sleepMs);
                }
            }
            logger.info("Finished streaming {} bytes", sent);
        };

        return ResponseEntity.ok()
                .contentType(org.springframework.http.MediaType.APPLICATION_OCTET_STREAM)
                .header(org.springframework.http.HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"stream-test.bin\"")
                .body(stream);
    }

}
