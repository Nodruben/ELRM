package com.example.searchorchestrator;

import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;

/**
 * Controller for handling search requests.
 * All code comments and documentation are written in English.
 */
@RestController
@RequestMapping("/search")
public class SearchController {

    private final SearchService searchService;
    private final StringRedisTemplate redisTemplate;

    public SearchController(SearchService searchService, StringRedisTemplate redisTemplate) {
        this.searchService = searchService;
        this.redisTemplate = redisTemplate;
    }

    /**
     * Endpoint to perform a search.
     *
     * @param request The search request.
     * @return The search result.
     */
    @PostMapping
    public SearchResponse search(@RequestBody SearchRequest request) {
        // Normalize the search query by trimming whitespace and lowercasing
        String normalizedQuery = request.getQuery() != null ? request.getQuery().trim().toLowerCase() : "";

        // Hash the normalized query to use as a Redis key
        String cacheKey = hashQuery(normalizedQuery);

        // Check if the response exists in Redis cache
        String cachedResponse = redisTemplate.opsForValue().get(cacheKey);

        if (cachedResponse != null) {
            // Cache hit: return immediately
            return new SearchResponse(cachedResponse, "redis-cache");
        }

        // Cache miss: proceed with the external call via SearchService
        SearchResponse responseFromEngine = searchService.search(request);

        if (responseFromEngine != null && responseFromEngine.getResult() != null) {
            // Save the response object in Redis with a TTL of 1 hour
            redisTemplate.opsForValue().set(cacheKey, responseFromEngine.getResult(), Duration.ofHours(1));
        }

        return responseFromEngine;
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
