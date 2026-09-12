package com.pulseai.service;

import com.pulseai.dto.*;
import com.pulseai.entity.EmergingIssue;
import com.pulseai.entity.Ticket;
import com.pulseai.external.MLServiceClient;
import com.pulseai.repository.TicketRepository;
import com.pulseai.repository.EmergingIssueRepository;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
@Transactional
public class AnalyticsService {
    
    private static final Logger log = LoggerFactory.getLogger(AnalyticsService.class);
    
    @Autowired
    private TicketRepository ticketRepository;
    
    @Autowired
    private EmergingIssueRepository emergingIssueRepository;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    public Map<String, Object> getTicketsSummary() {
        List<Ticket> allTickets = ticketRepository.findAll();
        
        Map<String, Object> summary = new HashMap<>();
        summary.put("total", allTickets.size());
        summary.put("byStatus", allTickets.stream()
                .collect(Collectors.groupingByConcurrent(Ticket::getStatus, Collectors.counting())));
        summary.put("byPriority", allTickets.stream()
                .collect(Collectors.groupingByConcurrent(Ticket::getPriority, Collectors.counting())));
        summary.put("avgSentiment", allTickets.stream()
                .mapToDouble(t -> t.getSentimentScore() != null ? t.getSentimentScore() : 0.0)
                .average()
                .orElse(0.0));
        
        return summary;
    }
    
    public Map<String, Object> getIncidentsSummary() {
        List<EmergingIssue> activeIssues = emergingIssueRepository.findActiveIssues();
        
        Map<String, Object> summary = new HashMap<>();
        summary.put("active", activeIssues.size());
        summary.put("bySeverity", activeIssues.stream()
                .collect(Collectors.groupingByConcurrent(EmergingIssue::getSeverity, Collectors.counting())));
        summary.put("byStatus", activeIssues.stream()
                .collect(Collectors.groupingByConcurrent(EmergingIssue::getStatus, Collectors.counting())));
        summary.put("critical", activeIssues.stream()
                .filter(i -> "CRITICAL".equals(i.getSeverity()))
                .count());
        
        return summary;
    }
    
    public List<Map<String, Object>> clusterAndDetectOutliers(Long minTickets) {
        List<Ticket> tickets = ticketRepository.findAll();
        
        if (tickets.size() < minTickets) {
            log.warn("Not enough tickets for clustering: {}", tickets.size());
            return new ArrayList<>();
        }
        
        try {
            // Generate embeddings for all tickets
            List<String> texts = tickets.stream()
                    .map(t -> t.getTitle() + " " + (t.getDescription() != null ? t.getDescription() : ""))
                    .collect(Collectors.toList());
            
            log.info("Generating embeddings for {} tickets", texts.size());
            // Note: In production, batch this via ML service
            
            // For now, return summary per cluster
            return tickets.stream()
                    .map(t -> {
                        Map<String, Object> item = new HashMap<>();
                        item.put("ticketId", t.getId());
                        item.put("title", t.getTitle());
                        item.put("clusterId", t.getId() % 3); // Dummy clustering
                        item.put("outlierScore", Math.random());
                        return item;
                    })
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.error("Error in clustering: {}", e.getMessage());
            return new ArrayList<>();
        }
    }
    
    public Map<String, Object> getAnomalies(int threshold) {
        List<Ticket> allTickets = ticketRepository.findAll();
        
        List<Ticket> anomalous = allTickets.stream()
                .filter(t -> t.getSentimentScore() != null && t.getSentimentScore() < threshold)
                .collect(Collectors.toList());
        
        Map<String, Object> result = new HashMap<>();
        result.put("total_anomalies", anomalous.size());
        result.put("percentage", (anomalous.size() * 100.0) / allTickets.size());
        result.put("anomalous_tickets", anomalous.stream()
                .map(t -> Map.of("id", t.getId(), "title", t.getTitle(), "score", t.getSentimentScore()))
                .collect(Collectors.toList()));
        
        return result;
    }
}
