import { useEffect, useState } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { Ticket, AlertTriangle, AlertOctagon, TrendingDown } from 'lucide-react';
import { API, apiFetch } from '../api';

interface OverviewData {
  total_tickets: number;
  active_issues: number;
  critical_issues: number;
  avg_sentiment: number;
  tickets_today: number;
  tickets_this_hour: number;
  top_categories: { category: string; count: number }[];
  sentiment_distribution: Record<string, number>;
}

interface VolumeSeries {
  series: { timestamp: string; volume: number; baseline: number }[];
}

const PIE_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#64748b'];

export default function OverviewPage() {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [volumeData, setVolumeData] = useState<VolumeSeries | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [ov, vol] = await Promise.all([
        apiFetch<OverviewData>(API.overview()),
        apiFetch<VolumeSeries>(API.volumeSeries('hours=24&interval=1h')),
      ]);
      setOverview(ov);
      setVolumeData(vol);
    } catch (err) {
      console.error('Failed to fetch overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !overview) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
      </div>
    );
  }

  const sentimentLabel = overview.avg_sentiment >= 0.1
    ? 'Positive' : overview.avg_sentiment <= -0.1
      ? 'Negative' : 'Neutral';

  const chartData = volumeData?.series.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    volume: p.volume,
    baseline: p.baseline,
  })) || [];

  const pieData = overview.top_categories.map((c) => ({
    name: c.category.replace('_', ' '),
    value: c.count,
  }));

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Dashboard Overview</h2>
        <p className="page-subtitle">Real-time support intelligence for CloudFlow Analytics</p>
      </div>

      <div className="page-content">
        {/* Metric Cards */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-card-header">
              <span className="metric-card-label">Total Tickets</span>
              <div className="metric-card-icon blue"><Ticket size={18} /></div>
            </div>
            <div className="metric-card-value">{overview.total_tickets.toLocaleString()}</div>
            <div className="metric-card-change">{overview.tickets_today} today · {overview.tickets_this_hour} this hour</div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <span className="metric-card-label">Active Issues</span>
              <div className="metric-card-icon orange"><AlertTriangle size={18} /></div>
            </div>
            <div className="metric-card-value">{overview.active_issues}</div>
            <div className="metric-card-change">Emerging problems detected</div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <span className="metric-card-label">Critical Issues</span>
              <div className="metric-card-icon red"><AlertOctagon size={18} /></div>
            </div>
            <div className="metric-card-value" style={{ color: overview.critical_issues > 0 ? 'var(--color-critical)' : undefined }}>
              {overview.critical_issues}
            </div>
            <div className={`metric-card-change ${overview.critical_issues > 0 ? 'negative' : ''}`}>
              {overview.critical_issues > 0 ? 'Immediate attention needed' : 'All clear'}
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <span className="metric-card-label">Avg Sentiment</span>
              <div className={`metric-card-icon ${overview.avg_sentiment <= -0.1 ? 'red' : 'green'}`}>
                <TrendingDown size={18} />
              </div>
            </div>
            <div className="metric-card-value">{overview.avg_sentiment.toFixed(2)}</div>
            <div className={`metric-card-change ${overview.avg_sentiment <= -0.1 ? 'negative' : 'positive'}`}>
              {sentimentLabel}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="card">
            <div className="card-header">
              <span className="card-title">Ticket Volume vs Baseline (24h)</span>
            </div>
            <div className="card-body">
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a3152" />
                    <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1f35',
                        border: '1px solid #2a3152',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="baseline"
                      stroke="#64748b"
                      fill="rgba(100, 116, 139, 0.1)"
                      strokeDasharray="4 4"
                      name="Baseline"
                    />
                    <Area
                      type="monotone"
                      dataKey="volume"
                      stroke="#3b82f6"
                      fill="rgba(59, 130, 246, 0.2)"
                      strokeWidth={2}
                      name="Volume"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Categories</span>
            </div>
            <div className="card-body">
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((_, index) => (
                        <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1f35',
                        border: '1px solid #2a3152',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                    <Legend
                      wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
