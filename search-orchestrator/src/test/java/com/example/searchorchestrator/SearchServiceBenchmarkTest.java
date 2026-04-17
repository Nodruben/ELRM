package com.example.searchorchestrator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.ReactiveRedisConnectionFactory;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

@SpringBootTest
public class SearchServiceBenchmarkTest {

    @Autowired
    private RestClient.Builder restClientBuilder;

    @Autowired
    private SearchService searchService;

    @MockBean
    private RedisConnectionFactory redisConnectionFactory; // Mock Redis to avoid test errors when offline

    @MockBean
    private ReactiveRedisConnectionFactory reactiveRedisConnectionFactory; // Need to mock this as well for spring data redis auto config

    private MockRestServiceServer server;

    @BeforeEach
    public void setup() {
        server = MockRestServiceServer.bindTo(restClientBuilder).build();
    }

    @Test
    public void testBenchmark() {
        System.out.println("Starting benchmark...");
        SearchRequest req = new SearchRequest("test");

        server.expect(org.springframework.test.web.client.ExpectedCount.manyTimes(), requestTo("http://localhost:8000/reason"))
            .andExpect(method(HttpMethod.POST))
            .andRespond(withSuccess("Reasoning result", MediaType.TEXT_PLAIN));

        long start = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            try {
                searchService.search(req);
            } catch (Exception e) {}
        }
        long end = System.currentTimeMillis();
        long totalTime = end - start;
        System.out.println("Total time for 1000 iterations: " + totalTime + "ms");
    }
}
