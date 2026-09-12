package com.pulseai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ClusteringRequest {
    private List<List<Double>> embeddings;
    
    public List<List<Double>> getEmbeddings() { return embeddings; }
    public void setEmbeddings(List<List<Double>> embeddings) { this.embeddings = embeddings; }
}
