import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { ArrowLeft, FileText, Info, Clock, Globe, Monitor, Users, CheckCircle2, UserPlus, Share2 } from 'lucide-react';
import { API, apiFetch } from '../api';

interface IssueDetail {
  issue: {
    id: string;
    title: string;
    summary: string;
    severity: string;
    status: string;
    confidence_score: number;
    ticket_count: number;
    volume_growth_pct: number;
    sentiment_avg: number;
    first_detected_at: string;
    last_updated_at: string;
    affected_demographics: {
      countries?: Record<string, number>;
      devices?: Record<string, number>;
      plans?: Record<string, number>;
    };
    key_terms: string[];
    root_cause_hypothesis: string | null;
    why_detected_breakdown: Record<string, string>;
  };
  timeline: {
    id: string;
    timestamp: string;
    event_type: string;
    title: string;
    description: string;
  }[];
  sample_tickets: {
    ticket_id: string;
    message: string;
    category: string;
    priority: string;
    channel: string;
    country: string;
    platform_device: string;
    customer_plan: string;
    sentiment_score: number;
    created_at: string;
    similarity_score: number;
  }[];
}

export default function ExplorerPage() {
  const { issueId } = useParams<{ issueId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<IssueDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [acknowledged, setAcknowledged] = useState(false);

  useEffect(() => {
    if (!issueId) return;
    const fetchDetail = async () => {
      try {
        const data = await apiFetch<IssueDetail>(API.issueDetail(issueId));
        setDetail(data);
      } catch (err) {
        console.error('Failed to fetch issue detail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
    const interval = setInterval(fetchDetail, 10000);
    return () => clearInterval(interval);
  }, [issueId]);

  if (!issueId) {
    return (
      <>
        <div className="page-header">
          <h2 className="page-title">Root Cause Explorer</h2>
          <p className="page-subtitle">Select an incident cluster to view forensic breakdown and affected tickets</p>
        </div>
        <div className="page-content">
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <Info size={40} style={{ color: 'var(--text-muted)', marginBottom: '12px' }} />
            <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Select an emerging incident from the list to investigate root cause</p>
          </div>
        </div>
      </>
    );
  }

  if (loading || !detail) {
    return <div className="loading-spinner"><div className="spinner" /></div>;
  }

  const { issue, timeline, sample_tickets } = detail;

  const countryData = Object.entries(issue.affected_demographics?.countries || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const deviceData = Object.entries(issue.affected_demographics?.devices || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const planData = Object.entries(issue.affected_demographics?.plans || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  return (
    <>
      <div className="page-header">
        <button
          onClick={() => navigate('/issues')}
          style={{
            background: 'none', border: 'none', color: 'var(--text-accent)',
            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '12.5px', marginBottom: '10px', padding: 0, fontWeight: 500
          }}
        >
          <ArrowLeft size={15} /> Back to Incidents
        </button>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 className="page-title">{issue.title}</h2>
            <span className={`severity-badge ${issue.severity.toLowerCase()}`}>{issue.severity}</span>
            <span className={`status-badge ${acknowledged ? 'investigating' : issue.status.toLowerCase()}`}>
              {acknowledged ? 'ACKNOWLEDGED' : issue.status}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setAcknowledged(true)}
              disabled={acknowledged}
              style={{
                padding: '6px 14px', fontSize: '12px', fontWeight: 600,
                background: acknowledged ? 'var(--color-success-bg)' : 'var(--bg-card)',
                color: acknowledged ? 'var(--color-success)' : 'var(--text-primary)',
                border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-sm)',
                cursor: acknowledged ? 'default' : 'pointer', display: 'flex', alignItems: 'center', gap: '6px'
              }}
            >
              <CheckCircle2 size={14} /> {acknowledged ? 'Acknowledged' : 'Acknowledge'}
            </button>
            <button
              style={{
                padding: '6px 14px', fontSize: '12px', fontWeight: 600,
                background: 'var(--bg-card)', color: 'var(--text-primary)',
                border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-sm)',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px'
              }}
            >
              <UserPlus size={14} /> Assign SRE Team
            </button>
            <button
              style={{
                padding: '6px 14px', fontSize: '12px', fontWeight: 600,
                background: 'var(--gradient-brand)', color: 'white',
                border: 'none', borderRadius: 'var(--radius-sm)',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px'
              }}
            >
              <Share2 size={14} /> Share Briefing
            </button>
          </div>
        </div>
      </div>

      <div className="page-content">
        {/* Incident Summary */}
        <div className="card" style={{ marginBottom: '14px' }}>
          <div className="card-header">
            <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileText size={15} color="var(--text-accent)" /> Incident Executive Briefing
            </span>
          </div>
          <div className="card-body">
            <p style={{ fontSize: '13.5px', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
              {issue.summary}
            </p>
            {issue.root_cause_hypothesis && (
              <p style={{ marginTop: '10px', fontSize: '13px', color: 'var(--text-muted)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Suspected Root Cause:</strong> {issue.root_cause_hypothesis}
              </p>
            )}
            {issue.key_terms.length > 0 && (
              <div style={{ marginTop: '10px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {issue.key_terms.map((term, i) => (
                  <span key={i} style={{
                    padding: '2px 8px', background: 'rgba(99,102,241,0.08)',
                    border: '1px solid var(--border-primary)', borderRadius: '12px',
                    fontSize: '11px', color: 'var(--text-accent)', fontFamily: 'var(--font-mono)'
                  }}>
                    #{term}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
          {/* Detection Logic */}
          <div className="explain-widget">
            <div className="explain-widget-title">
              <Info size={13} /> Detection Trigger Rules
            </div>
            {Object.entries(issue.why_detected_breakdown).map(([key, value]) => (
              <div key={key} className="explain-item">
                <span className="explain-item-icon">▸</span>
                <span>{value}</span>
              </div>
            ))}
          </div>

          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={15} /> Incident Audit Trail
              </span>
            </div>
            <div className="card-body">
              <div className="timeline">
                {timeline.map((event) => (
                  <div
                    key={event.id}
                    className={`timeline-item ${
                      event.event_type === 'SEVERITY_ESCALATED' ? 'critical' :
                      event.event_type === 'RESOLVED' ? 'success' : ''
                    }`}
                  >
                    <div className="timeline-time">
                      {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                    <div className="timeline-title">{event.title}</div>
                    <div className="timeline-desc">{event.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Demographics Charts */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '14px', marginBottom: '14px' }}>
          {[
            { title: 'Affected Regions', icon: <Globe size={13} />, data: countryData, color: '#3b82f6' },
            { title: 'Platforms & Devices', icon: <Monitor size={13} />, data: deviceData, color: '#6366f1' },
            { title: 'Customer Tiers', icon: <Users size={13} />, data: planData, color: '#10b981' },
          ].map((chart) => (
            <div key={chart.title} className="card">
              <div className="card-header">
                <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px' }}>
                  {chart.icon} {chart.title}
                </span>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={150}>
                  <BarChart data={chart.data} layout="vertical" margin={{ left: 45 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1b263b" />
                    <XAxis type="number" stroke="#64748b" fontSize={10} />
                    <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={10.5} width={40} />
                    <Tooltip contentStyle={{ backgroundColor: '#161f32', border: '1px solid #24314c', borderRadius: '6px', fontSize: '11.5px' }} />
                    <Bar dataKey="value" fill={chart.color} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
        </div>

        {/* Related Tickets */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Correlated Support Tickets ({sample_tickets.length})</span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket Ref</th>
                  <th>Customer Message</th>
                  <th>Channel</th>
                  <th>Country</th>
                  <th>Platform</th>
                  <th>Sentiment</th>
                  <th>Similarity</th>
                </tr>
              </thead>
              <tbody>
                {sample_tickets.map((t) => (
                  <tr key={t.ticket_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11.5px', color: 'var(--text-accent)' }}>{t.ticket_id}</td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {t.message}
                    </td>
                    <td>{t.channel}</td>
                    <td>{t.country}</td>
                    <td>{t.platform_device}</td>
                    <td style={{ color: t.sentiment_score < -0.3 ? 'var(--color-critical)' : 'var(--text-secondary)' }}>
                      {t.sentiment_score.toFixed(2)}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{(t.similarity_score * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
