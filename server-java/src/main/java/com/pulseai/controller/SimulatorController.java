package com.pulseai.controller;

import com.pulseai.service.SimulatorService;
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

import java.util.Map;

@RestController
@RequestMapping("/api/v1/simulator")
@Tag(name = "Simulator", description = "Incident simulator for testing")
@SecurityRequirement(name = "Bearer Authentication")
@Slf4j
public class SimulatorController {
    
    private static final Logger log = LoggerFactory.getLogger(SimulatorController.class);
    
    @Autowired
    private SimulatorService simulatorService;
    
    @PostMapping("/scenarios/visa-outage")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Simulate Visa payment outage scenario")
    public ResponseEntity<Map<String, String>> simulateVisaOutage() {
        log.warn("Initiating Visa outage simulation");
        simulatorService.simulateVisaOutage();
        return ResponseEntity.ok(Map.of("message", "Visa outage scenario created - check /api/v1/tickets"));
    }
    
    @PostMapping("/scenarios/login-bug")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Simulate login authentication bug scenario")
    public ResponseEntity<Map<String, String>> simulateLoginBug() {
        log.warn("Initiating login bug simulation");
        simulatorService.simulateLoginBug();
        return ResponseEntity.ok(Map.of("message", "Login bug scenario created - check /api/v1/tickets"));
    }
    
    @PostMapping("/scenarios/mobile-crash")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Simulate mobile app crash scenario")
    public ResponseEntity<Map<String, String>> simulateMobileCrash() {
        log.warn("Initiating mobile crash simulation");
        simulatorService.simulateMobileCrash();
        return ResponseEntity.ok(Map.of("message", "Mobile crash scenario created - check /api/v1/tickets"));
    }
    
    @PostMapping("/scenarios/normal-load")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Simulate normal ticket load")
    public ResponseEntity<Map<String, String>> simulateNormalLoad() {
        log.info("Initiating normal load simulation");
        simulatorService.simulateNormalLoad();
        return ResponseEntity.ok(Map.of("message", "Normal load scenario created - check /api/v1/tickets"));
    }
}
