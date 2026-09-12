package com.pulseai.external;

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
public class LLMServiceClient {
    
    private static final Logger log = LoggerFactory.getLogger(LLMServiceClient.class);
    
    @Value("${llm.api.key:}")
    private String llmApiKey;
    
    @Value("${llm.api.endpoint:https://api.openai.com/v1}")
    private String llmApiEndpoint;
    
    @Value("${llm.model:gpt-3.5-turbo}")
    private String llmModel;
    
    private final RestTemplate restTemplate;
    
    public LLMServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    public String generateAnswer(String query, List<String> context) {
        if (llmApiKey == null || llmApiKey.isBlank()) {
            log.warn("LLM API key not configured, returning empty answer");
            return "LLM service not configured";
        }
        
        try {
            String url = llmApiEndpoint + "/chat/completions";
            
            String systemPrompt = "You are a helpful support assistant. Use the provided context to answer questions.";
            String userMessage = "Context:\n" + String.join("\n", context) + "\n\nQuestion: " + query;
            
            Map<String, Object> payload = Map.of(
                "model", llmModel,
                "messages", List.of(
                    Map.of("role", "system", "content", systemPrompt),
                    Map.of("role", "user", "content", userMessage)
                ),
                "temperature", 0.7,
                "max_tokens", 500
            );
            
            Map<String, String> headers = Map.of(
                "Authorization", "Bearer " + llmApiKey,
                "Content-Type", "application/json"
            );
            
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, payload, Map.class);
            
            if (response != null && response.containsKey("choices")) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
                if (!choices.isEmpty()) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
                    String content = (String) message.get("content");
                    log.info("Generated LLM answer for query: {}", query.substring(0, Math.min(50, query.length())));
                    return content;
                }
            }
            
            return "Unable to generate answer";
        } catch (Exception e) {
            log.error("Error calling LLM service: {}", e.getMessage());
            return "Error generating answer: " + e.getMessage();
        }
    }
    
    public String generateTitle(String description) {
        if (llmApiKey == null || llmApiKey.isBlank()) {
            log.warn("LLM API key not configured, returning empty title");
            return "Unknown Issue";
        }
        
        try {
            String answer = generateAnswer("Generate a concise title (max 10 words) for: " + description, List.of());
            return answer.substring(0, Math.min(100, answer.length()));
        } catch (Exception e) {
            log.error("Error generating title: {}", e.getMessage());
            return "Generated Issue";
        }
    }
    
    public String generateRootCauseAnalysis(String description, List<String> similarTickets) {
        if (llmApiKey == null || llmApiKey.isBlank()) {
            return "Root cause analysis not available";
        }
        
        try {
            String contextStr = "Similar issues:\n" + String.join("\n", similarTickets);
            return generateAnswer("Analyze root cause for: " + description, List.of(contextStr));
        } catch (Exception e) {
            log.error("Error generating root cause analysis: {}", e.getMessage());
            return "Unable to analyze root cause";
        }
    }
}
