package com.pulseai.service;

import com.pulseai.entity.Ticket;
import com.pulseai.entity.User;
import com.pulseai.repository.TicketRepository;
import com.pulseai.repository.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@Slf4j
@Transactional
public class SimulatorService {
    
    private static final Logger log = LoggerFactory.getLogger(SimulatorService.class);
    
    @Autowired
    private TicketRepository ticketRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    public void simulateVisaOutage() {
        log.info("Simulating Visa outage scenario");
        User systemUser = getOrCreateSystemUser();
        
        String[] titles = {
            "Payment processing failing - Visa network",
            "Checkout timeout for credit card transactions",
            "Visa card declined - 3D Secure error",
            "Transaction stuck in pending state",
            "Recurring billing failed for Visa customers"
        };
        
        for (String title : titles) {
            Ticket ticket = new Ticket();
            ticket.setTitle(title);
            ticket.setDescription("Visa payment gateway unresponsive. Customers unable to complete purchases.");
            ticket.setStatus("OPEN");
            ticket.setPriority("CRITICAL");
            ticket.setCreatedBy(systemUser);
            ticket.setRawContent("Visa outage detected at " + LocalDateTime.now());
            ticket.setSentimentScore(-0.8);
            ticket.setCreatedAt(LocalDateTime.now());
            ticket.setUpdatedAt(LocalDateTime.now());
            
            ticketRepository.save(ticket);
        }
        
        log.info("Visa outage simulation: {} tickets created", titles.length);
    }
    
    public void simulateLoginBug() {
        log.info("Simulating login bug scenario");
        User systemUser = getOrCreateSystemUser();
        
        String[] titles = {
            "Login page blank after password reset",
            "Session token not being issued on successful login",
            "OAuth provider callback failing",
            "SSO integration returning 401 errors",
            "2FA authentication loop - endless redirect"
        };
        
        for (String title : titles) {
            Ticket ticket = new Ticket();
            ticket.setTitle(title);
            ticket.setDescription("Authentication layer returning incorrect responses. Users locked out.");
            ticket.setStatus("OPEN");
            ticket.setPriority("CRITICAL");
            ticket.setCreatedBy(systemUser);
            ticket.setRawContent("Login authentication failure detected");
            ticket.setSentimentScore(-0.9);
            ticket.setCreatedAt(LocalDateTime.now());
            ticket.setUpdatedAt(LocalDateTime.now());
            
            ticketRepository.save(ticket);
        }
        
        log.info("Login bug simulation: {} tickets created", titles.length);
    }
    
    public void simulateMobileCrash() {
        log.info("Simulating mobile app crash scenario");
        User systemUser = getOrCreateSystemUser();
        
        String[] titles = {
            "iOS app crashing on launch",
            "Android app force closing after update",
            "Mobile app memory leak consuming 2GB",
            "Push notification crashes app on Android 12",
            "Offline mode causing data sync errors"
        };
        
        for (String title : titles) {
            Ticket ticket = new Ticket();
            ticket.setTitle(title);
            ticket.setDescription("Mobile application stability issues. High crash rate on both platforms.");
            ticket.setStatus("OPEN");
            ticket.setPriority("CRITICAL");
            ticket.setCreatedBy(systemUser);
            ticket.setRawContent("Mobile app crash reports flooding in");
            ticket.setSentimentScore(-0.85);
            ticket.setCreatedAt(LocalDateTime.now());
            ticket.setUpdatedAt(LocalDateTime.now());
            
            ticketRepository.save(ticket);
        }
        
        log.info("Mobile crash simulation: {} tickets created", titles.length);
    }
    
    public void simulateNormalLoad() {
        log.info("Simulating normal ticket load");
        User systemUser = getOrCreateSystemUser();
        
        String[] normalTickles = {
            "Feature request: dark mode toggle",
            "UI improvement: optimize navigation flow",
            "Bug: avatar image not loading",
            "Performance: slow database queries",
            "Documentation: API endpoint examples",
            "Enhancement: export data to CSV",
            "Question: how to integrate with Slack"
        };
        
        for (String title : normalTickles) {
            Ticket ticket = new Ticket();
            ticket.setTitle(title);
            ticket.setDescription("Standard support ticket from user");
            ticket.setStatus("OPEN");
            ticket.setPriority("LOW");
            ticket.setCreatedBy(systemUser);
            ticket.setRawContent(title);
            ticket.setSentimentScore(0.2);
            ticket.setCreatedAt(LocalDateTime.now());
            ticket.setUpdatedAt(LocalDateTime.now());
            
            ticketRepository.save(ticket);
        }
        
        log.info("Normal load simulation: {} tickets created", normalTickles.length);
    }
    
    private User getOrCreateSystemUser() {
        Optional<User> existing = userRepository.findByUsername("system");
        if (existing.isPresent()) {
            return existing.get();
        }
        
        User systemUser = new User();
        systemUser.setUsername("system");
        systemUser.setEmail("system@pulseai.local");
        systemUser.setPassword("system");
        systemUser.setEnabled(true);
        systemUser.setCreatedAt(LocalDateTime.now());
        systemUser.setUpdatedAt(LocalDateTime.now());
        
        return userRepository.save(systemUser);
    }
}
