package com.example.searchorchestrator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class SearchOrchestratorApplication {

    public static void main(String[] args) {
        SpringApplication.run(SearchOrchestratorApplication.class, args);
    }

}
