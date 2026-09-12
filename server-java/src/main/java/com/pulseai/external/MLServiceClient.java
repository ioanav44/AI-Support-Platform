package com.pulseai.external;

import com.pulseai.dto.EmbeddingRequest;
import com.pulseai.dto.EmbeddingResponse;
import com.pulseai.dto.ClusteringRequest;
import com.pulseai.dto.ClusteringResponse;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Component
@Slf4j
public class MLServiceClient {
    
    private static final Logger log = LoggerFactory.getLogger(MLServiceClient.class);
    
    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;
    
    private final RestTemplate restTemplate;
    
    public MLServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    public String generateEmbedding(String text) {
        try {
            String url = mlServiceUrl + "/api/v1/embeddings/generate";
            EmbeddingRequest request = new EmbeddingRequest(text);
            
            EmbeddingResponse response = restTemplate.postForObject(url, request, EmbeddingResponse.class);
            log.debug("Generated embedding for text: {}", text.substring(0, Math.min(50, text.length())));
            
            if (response != null && response.getEmbedding() != null) {
                return convertEmbeddingToString(response.getEmbedding());
            }
            throw new RuntimeException("Empty embedding response");
        } catch (Exception e) {
            log.error("Error calling ML service for embedding: {}", e.getMessage());
            throw new RuntimeException("ML service unavailable", e);
        }
    }
    
    public Map<String, Object> clusterEmbeddings(List<String> embeddings) {
        try {
            String url = mlServiceUrl + "/api/v1/clustering/cluster";
            
            Map<String, Object> payload = Map.of("embeddings", embeddings);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, payload, Map.class);
            
            log.info("Clustered {} embeddings", embeddings.size());
            return response;
        } catch (Exception e) {
            log.error("Error calling ML service for clustering: {}", e.getMessage());
            return Map.of();
        }
    }
    
    public boolean isHealthy() {
        try {
            String url = mlServiceUrl + "/health";
            @SuppressWarnings("unchecked")
            var response = restTemplate.getForObject(url, java.util.Map.class);
            return "ok".equals(response.get("status"));
        } catch (Exception e) {
            log.warn("ML service health check failed: {}", e.getMessage());
            return false;
        }
    }
    
    private String convertEmbeddingToString(List<Double> embedding) {
        return "[" + embedding.stream()
                .map(Object::toString)
                .reduce((a, b) -> a + "," + b)
                .orElse("") + "]";
    }
}

