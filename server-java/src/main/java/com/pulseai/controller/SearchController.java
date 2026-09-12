package com.pulseai.controller;

import com.pulseai.dto.SearchRequest;
import com.pulseai.dto.TicketDTO;
import com.pulseai.entity.Ticket;
import com.pulseai.service.TicketService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/search")
@Tag(name = "Search", description = "Semantic search operations")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class SearchController {
    
    private static final Logger log = LoggerFactory.getLogger(SearchController.class);
    
    @Autowired
    private TicketService ticketService;
    
    @PostMapping("/semantic")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Perform semantic similarity search across tickets")
    public ResponseEntity<List<TicketDTO>> semanticSearch(@RequestBody SearchRequest request) {
        log.info("Semantic search request: query='{}', limit={}", request.getQuery(), request.getLimit());
        
        List<Ticket> results = ticketService.semanticSearch(request.getQuery(), request.getLimit());
        List<TicketDTO> dtos = results.stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
        
        return ResponseEntity.ok(dtos);
    }
    
    private TicketDTO mapToDTO(Ticket ticket) {
        TicketDTO dto = new TicketDTO();
        dto.setId(ticket.getId());
        dto.setTitle(ticket.getTitle());
        dto.setDescription(ticket.getDescription());
        dto.setStatus(ticket.getStatus());
        dto.setPriority(ticket.getPriority());
        dto.setCreatedAt(ticket.getCreatedAt().atZone(java.time.ZoneId.systemDefault()).toInstant().toEpochMilli());
        dto.setUpdatedAt(ticket.getUpdatedAt());
        if (ticket.getCreatedBy() != null) {
            dto.setCreatedByUsername(ticket.getCreatedBy().getUsername());
        }
        return dto;
    }
}
