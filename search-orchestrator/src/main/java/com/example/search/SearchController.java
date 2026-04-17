package com.example.search;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import java.util.Map;
import java.util.HashMap;

@RestController
public class SearchController {

    private static final Logger log = LoggerFactory.getLogger(SearchController.class);
    private final RestClient restClient;

    public SearchController() {
        this.restClient = RestClient.create();
    }

    @GetMapping("/search")
    public Map<String, Object> search(@RequestParam("query") String query) {
        Map<String, Object> response = new HashMap<>();
        String[] words = query.trim().split("\\s+");

        if (words.length <= 2) {
            log.info("FAST PATH - Routing decision: Bypass reasoning engine for query: '{}'", query);
            response.put("route", "FAST_PATH");
            response.put("message", "Bypassed reasoning engine");
            // Add actual fast path logic here if needed
            return response;
        } else {
            log.info("COMPLEX QUERY - Routing decision: Call reasoning engine for query: '{}'", query);
            response.put("route", "REASONING_ENGINE");

            try {
                // Assuming the python reasoning engine is running locally on some port, e.g., 8000
                // Adjust the URL based on the actual reasoning engine configuration
                String pythonEngineUrl = "http://localhost:8000/analyze-intent";

                Map<String, String> requestBody = new HashMap<>();
                requestBody.put("query", query);

                String engineResponse = restClient.post()
                        .uri(pythonEngineUrl)
                        .body(requestBody)
                        .retrieve()
                        .body(String.class);

                response.put("reasoningEngineResponse", engineResponse);
            } catch (Exception e) {
                log.error("Error calling reasoning engine", e);
                response.put("error", "Failed to call reasoning engine: " + e.getMessage());
            }

            return response;
        }
    }
}
