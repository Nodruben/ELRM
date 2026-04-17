package com.example.searchorchestrator;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.web.client.ClientHttpRequestFactories;
import org.springframework.boot.web.client.ClientHttpRequestFactorySettings;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.time.Duration;

@Service
public class SearchService {

    private static final Logger logger = LoggerFactory.getLogger(SearchService.class);

    private final RestClient restClient;
    private final String reasoningEngineUrl;
    private final String qdrantUrl;

    @Autowired
    public SearchService(
            RestClient.Builder restClientBuilder,
            @Value("${reasoning.engine.url}") String reasoningEngineUrl,
            @Value("${qdrant.url}") String qdrantUrl) {

        this.reasoningEngineUrl = reasoningEngineUrl;
        this.qdrantUrl = qdrantUrl;

        // Configure a strict timeout of 800ms for HTTP calls
        ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.DEFAULTS
                .withConnectTimeout(Duration.ofMillis(800))
                .withReadTimeout(Duration.ofMillis(800));

        ClientHttpRequestFactory requestFactory = ClientHttpRequestFactories.get(settings);

        this.restClient = restClientBuilder
                .requestFactory(requestFactory)
                .build();
    }

    // Constructor for testing with mock RestClient
    public SearchService(
            RestClient restClient,
            String reasoningEngineUrl,
            String qdrantUrl) {
        this.restClient = restClient;
        this.reasoningEngineUrl = reasoningEngineUrl;
        this.qdrantUrl = qdrantUrl;
    }

    @Cacheable(value = "search", key = "#request.query")
    public SearchResponse search(SearchRequest request) {
        try {
            // Attempt to call the Python reasoning engine first
            String result = restClient.post()
                    .uri(reasoningEngineUrl)
                    .body(request)
                    .retrieve()
                    .body(String.class);

            return new SearchResponse(result, "reasoning-engine");

        } catch (RestClientException e) {
            // Catch exception (timeout or connection error) and execute fallback
            logger.warn("Call to reasoning engine failed (timeout or unavailable). Using Qdrant fallback.", e);
            return fallbackSearch(request);
        }
    }

    private SearchResponse fallbackSearch(SearchRequest request) {
        try {
            // Standard text embedding search against Qdrant directly
            String result = restClient.post()
                    .uri(qdrantUrl)
                    .body(request)
                    .retrieve()
                    .body(String.class);
            return new SearchResponse(result, "qdrant-fallback");
        } catch (RestClientException e) {
            logger.error("Fallback Qdrant search also failed", e);
            throw e; // Standard spring boot error handling will catch and return 500
        }
    }
}
