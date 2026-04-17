package com.example.searchorchestrator;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;

/**
 * Controller for handling search requests.
 * All code comments and documentation are written in English.
 */
@RestController
public class SearchController {

    private final StringRedisTemplate redisTemplate;
    private final RestClient restClient;

    @Value("${reasoning.engine.url}")
    private String reasoningEngineUrl;

    public SearchController(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.restClient = RestClient.create();
    }

    /**
     * Endpoint to perform a search.
     *
     * @param query The search query string.
     * @return The search result.
     */
    @GetMapping("/search")
    public ResponseEntity<String> search(@RequestParam String query) {
        // Normalize the search query by trimming whitespace and lowercasing
        String normalizedQuery = query.trim().toLowerCase();

        // Hash the normalized query to use as a Redis key
        String cacheKey = hashQuery(normalizedQuery);

        // Check if the response exists in Redis cache
        String cachedResponse = redisTemplate.opsForValue().get(cacheKey);

        if (cachedResponse != null) {
            // Cache hit: return immediately
            return ResponseEntity.ok(cachedResponse);
        }

        // Cache miss: proceed with the external HTTP call to Python reasoning engine
        String responseFromEngine;
        try {
            responseFromEngine = restClient.get()
                    .uri(reasoningEngineUrl + "/search?query={query}", normalizedQuery)
                    .retrieve()
                    .body(String.class);
        } catch (Exception e) {
            // Handle error when calling reasoning engine
            return ResponseEntity.internalServerError().body("Error calling reasoning engine: " + e.getMessage());
        }

        if (responseFromEngine != null) {
            // Save the response object in Redis with a TTL of 1 hour
            redisTemplate.opsForValue().set(cacheKey, responseFromEngine, Duration.ofHours(1));
            return ResponseEntity.ok(responseFromEngine);
        } else {
            return ResponseEntity.noContent().build();
        }
    }

    /**
     * Hashes the given query using SHA-256.
     *
     * @param query The normalized query string.
     * @return The hashed query string.
     */
    private String hashQuery(String query) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(query.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(encodedhash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    /**
     * Helper method to convert a byte array to a hex string.
     *
     * @param hash The byte array.
     * @return The hex string representation.
     */
    private static String bytesToHex(byte[] hash) {
        StringBuilder hexString = new StringBuilder(2 * hash.length);
        for (byte b : hash) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }
}
