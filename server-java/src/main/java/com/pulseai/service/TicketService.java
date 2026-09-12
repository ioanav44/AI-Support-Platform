package com.pulseai.service;

import com.pulseai.entity.Ticket;
import com.pulseai.entity.User;
import com.pulseai.external.MLServiceClient;
import com.pulseai.repository.TicketRepository;
import com.pulseai.repository.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Slf4j
@Transactional
public class TicketService {
    
    private static final Logger log = LoggerFactory.getLogger(TicketService.class);
    
    @Autowired
    private TicketRepository ticketRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    public Ticket createTicket(String title, String description, String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        Ticket ticket = new Ticket();
        ticket.setTitle(title);
        ticket.setDescription(description);
        ticket.setStatus("OPEN");
        ticket.setPriority("MEDIUM");
        ticket.setCreatedBy(user);
        ticket.setCreatedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        
        ticket = ticketRepository.save(ticket);
        log.info("Ticket created: id={}, title={}", ticket.getId(), ticket.getTitle());
        
        try {
            String embedText = title + " " + description;
            String embedding = mlServiceClient.generateEmbedding(embedText);
            ticket.setEmbedding(embedding);
            ticket = ticketRepository.save(ticket);
            log.info("Embedding generated for ticket: id={}", ticket.getId());
        } catch (Exception e) {
            log.warn("Failed to generate embedding for ticket {}: {}", ticket.getId(), e.getMessage());
        }
        
        return ticket;
    }
    
    public Ticket updateTicket(Long id, String title, String description, String status) {
        Ticket ticket = ticketRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
        
        if (title != null) ticket.setTitle(title);
        if (description != null) ticket.setDescription(description);
        if (status != null) ticket.setStatus(status);
        ticket.setUpdatedAt(LocalDateTime.now());
        
        return ticketRepository.save(ticket);
    }
    
    public Ticket getTicketById(Long id) {
        return ticketRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
    }
    
    public List<Ticket> getAllTickets() {
        return ticketRepository.findAll();
    }
    
    public List<Ticket> getTicketsByStatus(String status) {
        return ticketRepository.findByStatus(status);
    }
    
    public void deleteTicket(Long id) {
        ticketRepository.deleteById(id);
        log.info("Ticket deleted: id={}", id);
    }
    
    public List<Ticket> semanticSearch(String query, int limit) {
        try {
            String queryEmbedding = mlServiceClient.generateEmbedding(query);
            List<Ticket> results = ticketRepository.findSimilarTickets(queryEmbedding, limit);
            log.info("Semantic search found {} tickets for query: '{}'", results.size(), query);
            return results;
        } catch (Exception e) {
            log.warn("Semantic search failed: {}", e.getMessage());
            return List.of();
        }
    }
}
