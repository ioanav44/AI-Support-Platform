package com.pulseai.repository;

import com.pulseai.entity.EmergingIssue;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EmergingIssueRepository extends JpaRepository<EmergingIssue, Long> {
    List<EmergingIssue> findByStatus(String status);
    List<EmergingIssue> findBySeverity(String severity);
    EmergingIssue findByTitle(String title);
    
    @Query("SELECT e FROM EmergingIssue e WHERE e.status != 'RESOLVED' ORDER BY e.severity DESC, e.createdAt DESC")
    List<EmergingIssue> findActiveIssues();
}
