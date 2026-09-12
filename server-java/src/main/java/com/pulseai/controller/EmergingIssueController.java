package com.pulseai.controller;

import com.pulseai.entity.EmergingIssue;
import com.pulseai.service.EmergingIssueService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/emerging-issues")
@Tag(name = "Emerging Issues", description = "Detected emerging issues and incidents")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class EmergingIssueController {
    
    private static final Logger log = LoggerFactory.getLogger(EmergingIssueController.class);
    
    @Autowired
    private EmergingIssueService emergingIssueService;
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Create new emerging issue")
    public ResponseEntity<EmergingIssue> createIssue(@RequestBody Map<String, String> request) {
        log.info("Creating emerging issue: {}", request.get("title"));
        
        EmergingIssue issue = emergingIssueService.createEmergingIssue(
                request.get("title"),
                request.get("description"),
                request.getOrDefault("severity", "MEDIUM"),
                request.get("whyDetected")
        );
        
        return ResponseEntity.status(HttpStatus.CREATED).body(issue);
    }
    
    @GetMapping("/active")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get active emerging issues")
    public ResponseEntity<List<EmergingIssue>> getActiveIssues() {
        List<EmergingIssue> issues = emergingIssueService.getActiveIssues();
        return ResponseEntity.ok(issues);
    }
    
    @GetMapping("/status/{status}")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get issues by status")
    public ResponseEntity<List<EmergingIssue>> getIssuesByStatus(@PathVariable String status) {
        List<EmergingIssue> issues = emergingIssueService.getIssuesByStatus(status);
        return ResponseEntity.ok(issues);
    }
    
    @GetMapping("/severity/{severity}")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get issues by severity")
    public ResponseEntity<List<EmergingIssue>> getIssuesBySeverity(@PathVariable String severity) {
        List<EmergingIssue> issues = emergingIssueService.getIssuesBySeverity(severity);
        return ResponseEntity.ok(issues);
    }
    
    @PostMapping("/{id}/resolve")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Mark issue as resolved")
    public ResponseEntity<EmergingIssue> resolveIssue(@PathVariable Long id) {
        log.info("Resolving issue: {}", id);
        EmergingIssue issue = emergingIssueService.markAsResolved(id);
        return ResponseEntity.ok(issue);
    }
    
    @PostMapping("/{issueId}/tickets/{ticketId}")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Link ticket to emerging issue")
    public ResponseEntity<Void> linkTicket(@PathVariable Long issueId, @PathVariable Long ticketId) {
        log.info("Linking ticket {} to issue {}", ticketId, issueId);
        emergingIssueService.linkTicketToIssue(issueId, ticketId);
        return ResponseEntity.noContent().build();
    }
}
