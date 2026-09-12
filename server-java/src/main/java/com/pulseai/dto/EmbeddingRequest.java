package com.pulseai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EmbeddingRequest {
    private String text;
    
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
}
