package com.pulseai.service;

import com.pulseai.entity.Ticket;
import com.pulseai.external.LLMServiceClient;
import com.pulseai.repository.TicketRepository;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Slf4j
@Transactional
public class RAGService {
    
    private static final Logger log = LoggerFactory.getLogger(RAGService.class);
    
    @Autowired
    private TicketService ticketService;
    
    @Autowired
    private LLMServiceClient llmServiceClient;
    
    public String queryKnowledgeBase(String query) {
        log.info("RAG query: {}", query);
        
        List<Ticket> relevantTickets = ticketService.semanticSearch(query, 5);
        
        List<String> contextItems = relevantTickets.stream()
                .map(t -> "Ticket #" + t.getId() + ": [" + t.getStatus() + "] " + 
                         t.getTitle() + " - " + 
                         (t.getDescription() != null ? t.getDescription() : ""))
                .limit(3)
                .collect(Collectors.toList());
        
        if (contextItems.isEmpty()) {
            return "No relevant data found in support tickets.";
        }
        
        String answer = llmServiceClient.generateAnswer(query, contextItems);
        log.info("Generated RAG answer for query: {}", query.substring(0, Math.min(50, query.length())));
        
        return answer;
    }
    
    public String askSupportData(String question) {
        return queryKnowledgeBase(question);
    }
}
