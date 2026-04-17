package com.example.searchorchestrator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withServerError;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

class SearchServiceTest {

    private SearchService searchService;
    private MockRestServiceServer server;

    @BeforeEach
    void setUp() {
        RestClient.Builder builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        RestClient restClient = builder.build();

        searchService = new SearchService(
                restClient,
                "http://localhost:8000/reason",
                "http://localhost:6333/collections/default/points/search"
        );
    }

    @Test
    void search_SuccessFromReasoningEngine() {
        SearchRequest request = new SearchRequest("test query");

        server.expect(requestTo("http://localhost:8000/reason"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("Reasoning result", MediaType.TEXT_PLAIN));

        SearchResponse response = searchService.search(request);

        assertEquals("Reasoning result", response.getResult());
        assertEquals("reasoning-engine", response.getSource());
        server.verify();
    }

    @Test
    void search_FallbackToQdrantOnFailure() {
        SearchRequest request = new SearchRequest("test query");

        // Simulate reasoning engine failure (e.g., timeout or server error)
        server.expect(requestTo("http://localhost:8000/reason"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        // Expect fallback to Qdrant
        server.expect(requestTo("http://localhost:6333/collections/default/points/search"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("Qdrant result", MediaType.TEXT_PLAIN));

        SearchResponse response = searchService.search(request);

        assertEquals("Qdrant result", response.getResult());
        assertEquals("qdrant-fallback", response.getSource());
        server.verify();
    }

    @Test
    void search_ThrowsExceptionWhenFallbackAlsoFails() {
        SearchRequest request = new SearchRequest("test query");

        // Simulate reasoning engine failure
        server.expect(requestTo("http://localhost:8000/reason"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        // Expect fallback to Qdrant, but it also fails
        server.expect(requestTo("http://localhost:6333/collections/default/points/search"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        assertThrows(RestClientException.class, () -> searchService.search(request));

        server.verify();
    }
}
