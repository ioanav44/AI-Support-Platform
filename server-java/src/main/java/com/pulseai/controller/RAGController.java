package com.pulseai.controller;

import com.pulseai.dto.RAGRequest;
import com.pulseai.dto.RAGResponse;
import com.pulseai.service.RAGService;
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

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/v1/rag")
@Tag(name = "RAG", description = "Retrieval-Augmented Generation - Ask Support Data")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class RAGController {
    
    private static final Logger log = LoggerFactory.getLogger(RAGController.class);
    
    @Autowired
    private RAGService ragService;
    
    @PostMapping("/query")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Query support data using RAG (Retrieval-Augmented Generation)")
    public ResponseEntity<RAGResponse> querySupport(@RequestBody RAGRequest request) {
        log.info("RAG query request: {}", request.getQuestion());
        
        String answer = ragService.askSupportData(request.getQuestion());
        
        RAGResponse response = new RAGResponse();
        response.setQuestion(request.getQuestion());
        response.setAnswer(answer);
        response.setTimestamp(LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/health")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Check RAG service health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("RAG service is operational");
    }
}
