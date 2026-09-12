package com.pulseai.security;

import io.jsonwebtoken.Jwts;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
class JwtTokenProviderTest {
    
    @Autowired
    private JwtTokenProvider tokenProvider;
    
    private String testUsername;
    
    @BeforeEach
    void setUp() {
        testUsername = "testuser";
    }
    
    @Test
    void testGenerateAccessToken() {
        String token = tokenProvider.generateAccessToken(testUsername);
        
        assertNotNull(token);
        assertFalse(token.isEmpty());
        assertTrue(tokenProvider.validateToken(token));
    }
    
    @Test
    void testGenerateRefreshToken() {
        String token = tokenProvider.generateRefreshToken(testUsername);
        
        assertNotNull(token);
        assertFalse(token.isEmpty());
        assertTrue(tokenProvider.validateToken(token));
    }
    
    @Test
    void testGetUsernameFromToken() {
        String token = tokenProvider.generateAccessToken(testUsername);
        String username = tokenProvider.getUsernameFromToken(token);
        
        assertEquals(testUsername, username);
    }
    
    @Test
    void testValidateToken() {
        String token = tokenProvider.generateAccessToken(testUsername);
        
        assertTrue(tokenProvider.validateToken(token));
    }
    
    @Test
    void testValidateInvalidToken() {
        String invalidToken = "invalid.token.here";
        
        assertFalse(tokenProvider.validateToken(invalidToken));
    }
}
