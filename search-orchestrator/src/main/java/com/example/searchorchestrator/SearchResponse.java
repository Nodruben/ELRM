package com.example.searchorchestrator;

public class SearchResponse {
    private String result;
    private String source;

    public SearchResponse() {}

    public SearchResponse(String result, String source) {
        this.result = result;
        this.source = source;
    }

    public String getResult() {
        return result;
    }

    public void setResult(String result) {
        this.result = result;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }
}
