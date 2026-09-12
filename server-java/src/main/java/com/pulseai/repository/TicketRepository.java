package com.pulseai.repository;

import com.pulseai.entity.Ticket;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TicketRepository extends JpaRepository<Ticket, Long> {
    List<Ticket> findByStatus(String status);
    List<Ticket> findByAssignedToId(Long userId);
    
    @Query(value = "SELECT * FROM tickets WHERE embedding IS NOT NULL " +
                   "ORDER BY embedding <-> CAST(:embedding AS vector(384)) LIMIT :limit", 
           nativeQuery = true)
    List<Ticket> findSimilarTickets(@Param("embedding") String embedding, @Param("limit") int limit);
}
