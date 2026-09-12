import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Shield, Search, ChevronRight, Filter } from 'lucide-react';
import { API, apiFetch } from '../api';

interface Issue {
  id: string;
  title: string;
  summary?: string;
  severity: string;
  status: string;
  confidence_score: number;
  ticket_count: number;
  volume_growth_pct: number;
  sentiment_avg: number;
  first_detected_at: string;
  key_terms?: string[];
}

export default function IssuesPage() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const navigate = useNavigate();

  const fetchIssues = async () => {
    try {
      const params = statusFilter !== 'all' ? `status=${statusFilter}` : '';
      const data = await apiFetch<{ issues: Issue[] }>(API.listIssues(params));
      setIssues(data.issues);
    } catch (err) {
      console.error('Failed to fetch issues:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, [statusFilter]);

  const updateIssueStatus = async (e: React.MouseEvent, issueId: string, newStatus: string) => {
    e.stopPropagation();
    try {
      await apiFetch(API.updateIssue(issueId), {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
    } catch (err) {
      console.warn('Backend offline, updating status locally');
    }
    setIssues((prev) =>
      prev.map((i) => (i.id === issueId ? { ...i, status: newStatus } : i))
    );
  };

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredIssues = issues.filter((issue) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      issue.title.toLowerCase().includes(q) ||
      (issue.summary && issue.summary.toLowerCase().includes(q)) ||
      issue.severity.toLowerCase().includes(q) ||
      issue.status.toLowerCase().includes(q) ||
      (issue.key_terms && issue.key_terms.some((t) => t.toLowerCase().includes(q)))
    );
  });

  const filters = [
    { value: 'all', label: 'All Statuses' },
    { value: 'DETECTED', label: 'Detected' },
    { value: 'INVESTIGATING', label: 'Investigating' },
    { value: 'MITIGATED', label: 'Mitigated' },
    { value: 'RESOLVED', label: 'Resolved' },
  ];

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Emerging Incidents</h2>
        <p className="page-subtitle">Real-time vector anomalies and clustered customer support incidents</p>
      </div>

      <div className="page-content">
        {/* Controls Toolbar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
          {/* Status Pills */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {filters.map((f) => (
              <button
                key={f.value}
                className={`sim-btn ${statusFilter === f.value ? 'active' : ''}`}
                onClick={() => setStatusFilter(f.value)}
                style={statusFilter === f.value ? { background: 'rgba(99,102,241,0.15)', borderColor: 'var(--border-accent)', color: 'var(--text-accent)' } : {}}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Search Bar */}
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search incidents or terms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '6px 12px 6px 32px',
                fontSize: '12.5px',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {loading ? (
          <div className="loading-spinner"><div className="spinner" /></div>
        ) : filteredIssues.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '50px 20px' }}>
            <Shield size={40} style={{ color: 'var(--color-success)', marginBottom: '12px' }} />
            <h3 style={{ fontSize: '16px', marginBottom: '6px' }}>No Matching Incidents</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '16px' }}>
              No active incident clusters match your selected status or search filter.
            </p>

            {(statusFilter !== 'all' || searchQuery) && (
              <button
                className="sim-btn"
                onClick={() => { setStatusFilter('all'); setSearchQuery(''); }}
                style={{ margin: '0 auto', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <Filter size={13} /> Reset Filters
              </button>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredIssues.map((issue) => (
              <div
                key={issue.id}
                className={`issue-card ${issue.severity.toLowerCase()}`}
                onClick={() => navigate(`/explorer/${issue.id}`)}
              >
                <div className="issue-card-header">
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span className={`severity-badge ${issue.severity.toLowerCase()}`}>
                        {issue.severity}
                      </span>
                      <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        ID: {issue.id.slice(0, 8)}
                      </span>
                    </div>

                    <h3 className="issue-card-title">
                      {issue.title}
                    </h3>

                    {issue.summary && (
                      <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: '1.4' }}>
                        {issue.summary}
                      </p>
                    )}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                    <select
                      value={issue.status}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => updateIssueStatus(e as unknown as React.MouseEvent, issue.id, e.target.value)}
                      style={{
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border-primary)',
                        color: 'var(--text-primary)',
                        fontSize: '11px',
                        fontWeight: 600,
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer',
                        outline: 'none',
                      }}
                    >
                      <option value="DETECTED">DETECTED</option>
                      <option value="INVESTIGATING">INVESTIGATING</option>
                      <option value="MITIGATED">MITIGATED</option>
                      <option value="RESOLVED">RESOLVED</option>
                    </select>

                    <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
                  </div>
                </div>

                <div className="issue-card-meta">
                  <div className="issue-meta-item">
                    <Clock size={13} />
                    First detected: {formatTime(issue.first_detected_at)}
                  </div>

                  {issue.key_terms && issue.key_terms.length > 0 && (
                    <div style={{ display: 'flex', gap: '4px', marginLeft: 'auto' }}>
                      {issue.key_terms.map((term, i) => (
                        <span key={i} style={{
                          padding: '1px 6px',
                          background: 'var(--bg-elevated)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '4px',
                          fontSize: '10.5px',
                          color: 'var(--text-accent)',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          #{term}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="issue-card-stats">
                  <div className="issue-stat">
                    <span className="issue-stat-label">Ticket Volume</span>
                    <span className="issue-stat-value">{issue.ticket_count}</span>
                  </div>
                  <div className="issue-stat">
                    <span className="issue-stat-label">Volume Spike</span>
                    <span className="issue-stat-value spike">+{issue.volume_growth_pct.toFixed(0)}%</span>
                  </div>
                  <div className="issue-stat">
                    <span className="issue-stat-label">Vector Confidence</span>
                    <span className="issue-stat-value">{(issue.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="issue-stat">
                    <span className="issue-stat-label">Avg Sentiment</span>
                    <span className="issue-stat-value" style={{ color: issue.sentiment_avg < -0.3 ? 'var(--color-critical)' : 'var(--text-secondary)' }}>
                      {issue.sentiment_avg.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
