package com.pulseai.controller;

import com.pulseai.service.AnalyticsService;
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
import java.util.Map;

@RestController
@RequestMapping("/api/v1/analytics")
@Tag(name = "Analytics", description = "System analytics and reporting")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class AnalyticsController {
    
    private static final Logger log = LoggerFactory.getLogger(AnalyticsController.class);
    
    @Autowired
    private AnalyticsService analyticsService;
    
    @GetMapping("/tickets/summary")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get tickets summary statistics")
    public ResponseEntity<Map<String, Object>> getTicketsSummary() {
        log.info("Fetching tickets summary");
        return ResponseEntity.ok(analyticsService.getTicketsSummary());
    }
    
    @GetMapping("/incidents/summary")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get incidents summary statistics")
    public ResponseEntity<Map<String, Object>> getIncidentsSummary() {
        log.info("Fetching incidents summary");
        return ResponseEntity.ok(analyticsService.getIncidentsSummary());
    }
    
    @GetMapping("/clustering")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get ticket clustering and outliers")
    public ResponseEntity<List<Map<String, Object>>> getClustering(
            @RequestParam(defaultValue = "5") Long minTickets) {
        log.info("Fetching clustering analysis");
        return ResponseEntity.ok(analyticsService.clusterAndDetectOutliers(minTickets));
    }
    
    @GetMapping("/anomalies")
    @PreAuthorize("hasAnyRole('ANALYST', 'ADMIN')")
    @Operation(summary = "Get anomaly detection results")
    public ResponseEntity<Map<String, Object>> getAnomalies(
            @RequestParam(defaultValue = "3") int threshold) {
        log.info("Fetching anomalies");
        return ResponseEntity.ok(analyticsService.getAnomalies(threshold));
    }
}
