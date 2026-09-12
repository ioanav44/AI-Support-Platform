package com.pulseai.controller;

import com.pulseai.entity.Ticket;
import com.pulseai.service.TicketService;
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
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/tickets")
@Tag(name = "Tickets", description = "Ticket management endpoints")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class TicketController {
    
    private static final Logger log = LoggerFactory.getLogger(TicketController.class);
    
    @Autowired
    private TicketService ticketService;
    
    @PostMapping
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Create a new ticket")
    public ResponseEntity<Ticket> createTicket(
            @RequestBody Map<String, String> request,
            Authentication authentication) {
        log.info("Creating ticket by user: {}", authentication.getName());
        
        Ticket ticket = ticketService.createTicket(
                request.get("title"),
                request.get("description"),
                authentication.getName()
        );
        
        return ResponseEntity.status(HttpStatus.CREATED).body(ticket);
    }
    
    @GetMapping
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get all tickets")
    public ResponseEntity<List<Ticket>> getAllTickets() {
        List<Ticket> tickets = ticketService.getAllTickets();
        return ResponseEntity.ok(tickets);
    }
    
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get ticket by ID")
    public ResponseEntity<Ticket> getTicketById(@PathVariable Long id) {
        Ticket ticket = ticketService.getTicketById(id);
        return ResponseEntity.ok(ticket);
    }
    
    @GetMapping("/status/{status}")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get tickets by status")
    public ResponseEntity<List<Ticket>> getTicketsByStatus(@PathVariable String status) {
        List<Ticket> tickets = ticketService.getTicketsByStatus(status);
        return ResponseEntity.ok(tickets);
    }
    
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Update ticket")
    public ResponseEntity<Ticket> updateTicket(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        log.info("Updating ticket: id={}", id);
        
        Ticket ticket = ticketService.updateTicket(
                id,
                request.get("title"),
                request.get("description"),
                request.get("status")
        );
        
        return ResponseEntity.ok(ticket);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Delete ticket (ADMIN only)")
    public ResponseEntity<Void> deleteTicket(@PathVariable Long id) {
        log.info("Deleting ticket: id={}", id);
        ticketService.deleteTicket(id);
        return ResponseEntity.noContent().build();
    }
}
