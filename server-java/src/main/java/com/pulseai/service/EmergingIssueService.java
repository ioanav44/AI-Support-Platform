package com.pulseai.service;

import com.pulseai.entity.EmergingIssue;
import com.pulseai.entity.Ticket;
import com.pulseai.repository.EmergingIssueRepository;
import com.pulseai.repository.TicketRepository;
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
public class EmergingIssueService {
    
    private static final Logger log = LoggerFactory.getLogger(EmergingIssueService.class);
    
    @Autowired
    private EmergingIssueRepository emergingIssueRepository;
    
    @Autowired
    private TicketRepository ticketRepository;
    
    public EmergingIssue createEmergingIssue(String title, String description, 
                                             String severity, String whyDetected) {
        EmergingIssue issue = new EmergingIssue();
        issue.setTitle(title);
        issue.setDescription(description);
        issue.setSeverity(severity);
        issue.setWhyDetected(whyDetected);
        issue.setStatus("NEW");
        issue.setCreatedAt(LocalDateTime.now());
        issue.setUpdatedAt(LocalDateTime.now());
        
        issue = emergingIssueRepository.save(issue);
        log.info("Emerging issue created: id={}, title={}, severity={}", 
                issue.getId(), issue.getTitle(), issue.getSeverity());
        
        return issue;
    }
    
    public void linkTicketToIssue(Long issueId, Long ticketId) {
        EmergingIssue issue = emergingIssueRepository.findById(issueId)
                .orElseThrow(() -> new RuntimeException("Issue not found"));
        
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found"));
        
        issue.addTicket(ticket);
        issue.setLastOccurrence(LocalDateTime.now());
        issue.setUpdatedAt(LocalDateTime.now());
        
        emergingIssueRepository.save(issue);
        log.debug("Linked ticket {} to issue {}", ticketId, issueId);
    }
    
    public List<EmergingIssue> getActiveIssues() {
        return emergingIssueRepository.findActiveIssues();
    }
    
    public List<EmergingIssue> getIssuesByStatus(String status) {
        return emergingIssueRepository.findByStatus(status);
    }
    
    public List<EmergingIssue> getIssuesBySeverity(String severity) {
        return emergingIssueRepository.findBySeverity(severity);
    }
    
    public EmergingIssue markAsResolved(Long id) {
        EmergingIssue issue = emergingIssueRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Issue not found"));
        
        issue.markAsResolved();
        return emergingIssueRepository.save(issue);
    }
}
