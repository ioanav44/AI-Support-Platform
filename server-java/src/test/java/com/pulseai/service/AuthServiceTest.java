package com.pulseai.service;

import com.pulseai.dto.AuthResponse;
import com.pulseai.dto.LoginRequest;
import com.pulseai.dto.RegisterRequest;
import com.pulseai.entity.Role;
import com.pulseai.entity.User;
import com.pulseai.repository.RoleRepository;
import com.pulseai.repository.UserRepository;
import com.pulseai.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private RoleRepository roleRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @Mock
    private AuthenticationManager authenticationManager;
    
    @Mock
    private JwtTokenProvider tokenProvider;
    
    @InjectMocks
    private AuthService authService;
    
    private RegisterRequest registerRequest;
    private User testUser;
    private Role analystRole;
    
    @BeforeEach
    void setUp() {
        registerRequest = new RegisterRequest("testuser", "test@example.com", "password123");
        
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setPassword("hashed_password");
        testUser.setEnabled(true);
        
        analystRole = new Role();
        analystRole.setId(2L);
        analystRole.setName(Role.RoleType.ANALYST);
        analystRole.setDescription("Support analyst");
    }
    
    @Test
    void testRegisterSuccess() {
        // Arrange
        when(userRepository.existsByUsername(anyString())).thenReturn(false);
        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(passwordEncoder.encode(anyString())).thenReturn("hashed_password");
        when(roleRepository.findByName(Role.RoleType.ANALYST)).thenReturn(Optional.of(analystRole));
        when(userRepository.save(any(User.class))).thenReturn(testUser);
        when(tokenProvider.generateAccessToken(anyString())).thenReturn("access_token");
        when(tokenProvider.generateRefreshToken(anyString())).thenReturn("refresh_token");
        when(tokenProvider.getExpirationTime()).thenReturn(900000L);
        
        // Act
        AuthResponse response = authService.register(registerRequest);
        
        // Assert
        assertNotNull(response);
        assertEquals("testuser", response.getUsername());
        assertEquals("test@example.com", response.getEmail());
        assertEquals("access_token", response.getAccessToken());
        assertEquals("refresh_token", response.getRefreshToken());
        verify(userRepository, times(1)).save(any(User.class));
    }
    
    @Test
    void testRegisterUsernameTaken() {
        // Arrange
        when(userRepository.existsByUsername(anyString())).thenReturn(true);
        
        // Act & Assert
        assertThrows(RuntimeException.class, () -> authService.register(registerRequest));
    }
    
    @Test
    void testLoginSuccess() {
        // Arrange
        LoginRequest loginRequest = new LoginRequest("testuser", "password123");
        Authentication auth = mock(Authentication.class);
        when(auth.getName()).thenReturn("testuser");
        when(authenticationManager.authenticate(any())).thenReturn(auth);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(tokenProvider.generateAccessToken(any(Authentication.class))).thenReturn("access_token");
        when(tokenProvider.generateRefreshToken("testuser")).thenReturn("refresh_token");
        when(tokenProvider.getExpirationTime()).thenReturn(900000L);
        
        // Act
        AuthResponse response = authService.login(loginRequest);
        
        // Assert
        assertNotNull(response);
        assertEquals("testuser", response.getUsername());
        assertEquals("access_token", response.getAccessToken());
        verify(authenticationManager, times(1)).authenticate(any());
    }
    
    @Test
    void testRefreshTokenSuccess() {
        // Arrange
        when(tokenProvider.validateToken("refresh_token")).thenReturn(true);
        when(tokenProvider.getUsernameFromToken("refresh_token")).thenReturn("testuser");
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(tokenProvider.generateAccessToken("testuser")).thenReturn("new_access_token");
        when(tokenProvider.generateRefreshToken("testuser")).thenReturn("new_refresh_token");
        when(tokenProvider.getExpirationTime()).thenReturn(900000L);
        
        // Act
        AuthResponse response = authService.refreshAccessToken("refresh_token");
        
        // Assert
        assertNotNull(response);
        assertEquals("new_access_token", response.getAccessToken());
        assertEquals("new_refresh_token", response.getRefreshToken());
    }
}
