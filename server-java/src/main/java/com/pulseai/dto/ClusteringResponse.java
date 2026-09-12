package com.pulseai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ClusteringResponse {
    private List<Integer> clusterLabels;
    private List<Double> outlierScores;
    private int nCluster;
    
    public List<Integer> getClusterLabels() { return clusterLabels; }
    public void setClusterLabels(List<Integer> clusterLabels) { this.clusterLabels = clusterLabels; }
    
    public List<Double> getOutlierScores() { return outlierScores; }
    public void setOutlierScores(List<Double> outlierScores) { this.outlierScores = outlierScores; }
    
    public int getNCluster() { return nCluster; }
    public void setNCluster(int nCluster) { this.nCluster = nCluster; }
}
