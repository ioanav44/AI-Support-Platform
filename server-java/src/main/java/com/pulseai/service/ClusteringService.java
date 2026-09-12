package com.pulseai.service;

import com.pulseai.entity.Ticket;
import com.pulseai.entity.EmergingIssue;
import com.pulseai.external.MLServiceClient;
import com.pulseai.repository.TicketRepository;
import com.pulseai.repository.EmergingIssueRepository;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@Transactional
public class ClusteringService {
    
    private static final Logger log = LoggerFactory.getLogger(ClusteringService.class);
    
    @Autowired
    private TicketRepository ticketRepository;
    
    @Autowired
    private EmergingIssueRepository emergingIssueRepository;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    @Scheduled(fixedRate = 300000, initialDelay = 10000) // Every 5 minutes after 10s startup delay
    public void runClusteringPipeline() {
        log.info("Starting clustering pipeline...");
        
        try {
            List<Ticket> tickets = ticketRepository.findAll();
            
            if (tickets.isEmpty()) {
                log.debug("No tickets to cluster");
                return;
            }
            
            List<Ticket> ticketsWithEmbedding = tickets.stream()
                    .filter(t -> t.getEmbedding() != null && !t.getEmbedding().isBlank())
                    .toList();
            
            if (ticketsWithEmbedding.isEmpty()) {
                log.debug("No tickets with embeddings to cluster");
                return;
            }
            
            log.info("Clustering {} tickets with embeddings", ticketsWithEmbedding.size());
            
            List<String> embeddings = ticketsWithEmbedding.stream()
                    .map(Ticket::getEmbedding)
                    .toList();
            
            Map<String, Object> clusterResult = mlServiceClient.clusterEmbeddings(embeddings);
            
            if (clusterResult == null || clusterResult.isEmpty()) {
                log.warn("Clustering returned empty result");
                return;
            }
            
            List<Integer> clusterLabels = (List<Integer>) clusterResult.get("cluster_labels");
            List<Double> outlierScores = (List<Double>) clusterResult.get("outlier_scores");
            
            for (int i = 0; i < ticketsWithEmbedding.size(); i++) {
                Ticket ticket = ticketsWithEmbedding.get(i);
                if (clusterLabels != null && i < clusterLabels.size()) {
                    Integer clusterId = clusterLabels.get(i);
                    ticket.setClusterId(clusterId);
                }
                if (outlierScores != null && i < outlierScores.size()) {
                    Double score = outlierScores.get(i);
                    ticket.setOutlierScore(score);
                    ticket.setIsAnomaly(score > 0.5);
                }
                ticketRepository.save(ticket);
            }
            
            detectAndCreateEmergingIssues(ticketsWithEmbedding, clusterLabels);
            
            log.info("Clustering pipeline completed successfully");
            
        } catch (Exception e) {
            log.error("Error during clustering pipeline", e);
        }
    }
    
    private void detectAndCreateEmergingIssues(List<Ticket> tickets, List<Integer> clusterLabels) {
        if (clusterLabels == null || clusterLabels.isEmpty()) {
            return;
        }
        
        Map<Integer, List<Ticket>> clusterMap = new java.util.HashMap<>();
        for (int i = 0; i < tickets.size(); i++) {
            Integer clusterId = clusterLabels.get(i);
            if (clusterId != null && clusterId >= 0) {
                clusterMap.computeIfAbsent(clusterId, k -> new java.util.ArrayList<>()).add(tickets.get(i));
            }
        }
        
        for (Map.Entry<Integer, List<Ticket>> entry : clusterMap.entrySet()) {
            int clusterId = entry.getKey();
            List<Ticket> clusterTickets = entry.getValue();
            
            if (clusterTickets.size() >= 3) {
                String existingIssueTitle = generateIssueTitle(clusterTickets);
                
                EmergingIssue existingIssue = emergingIssueRepository
                        .findByTitle(existingIssueTitle);
                
                if (existingIssue == null) {
                    EmergingIssue issue = new EmergingIssue();
                    issue.setTitle(existingIssueTitle);
                    issue.setDescription(generateIssueDescription(clusterTickets));
                    issue.setSeverity("MEDIUM");
                    issue.setStatus("DETECTED");
                    issue.setDetectedAt(LocalDateTime.now());
                    issue.setTickets(new java.util.HashSet<>(clusterTickets));
                    
                    emergingIssueRepository.save(issue);
                    log.info("Created emerging issue: {}", existingIssueTitle);
                }
            }
        }
    }
    
    private String generateIssueTitle(List<Ticket> tickets) {
        int maxLength = 50;
        String commonTerms = extractCommonTerms(tickets);
        if (commonTerms.length() > maxLength) {
            return commonTerms.substring(0, maxLength) + "...";
        }
        return commonTerms.isEmpty() ? "Cluster Issue (Tickets: " + tickets.size() + ")" : commonTerms;
    }
    
    private String generateIssueDescription(List<Ticket> tickets) {
        return "Emerging issue detected in cluster with " + tickets.size() + " related tickets. " +
               "Key topics: " + extractCommonTerms(tickets);
    }
    
    private String extractCommonTerms(List<Ticket> tickets) {
        String combined = tickets.stream()
                .map(t -> t.getTitle().toLowerCase())
                .reduce("", (a, b) -> a + " " + b);
        
        String[] words = combined.split("\\s+");
        Map<String, Integer> wordCount = new java.util.HashMap<>();
        
        for (String word : words) {
            if (word.length() > 3 && !isCommonWord(word)) {
                wordCount.put(word, wordCount.getOrDefault(word, 0) + 1);
            }
        }
        
        return wordCount.entrySet().stream()
                .filter(e -> e.getValue() >= 2)
                .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
                .limit(3)
                .map(Map.Entry::getKey)
                .reduce((a, b) -> a + ", " + b)
                .orElse("Multiple issues");
    }
    
    private boolean isCommonWord(String word) {
        return word.matches("(the|and|for|with|from|to|of|in|at|on|is|are|was|were|be|have|has)");
    }
}
