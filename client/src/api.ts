const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const API = {
  ingestTicket: () => `${API_BASE}/api/v1/tickets`,
  listTickets: (params: string) => `${API_BASE}/api/v1/tickets?${params}`,

  listIssues: (params?: string) => `${API_BASE}/api/v1/issues${params ? '?' + params : ''}`,
  issueDetail: (id: string) => `${API_BASE}/api/v1/issues/${id}`,
  updateIssue: (id: string) => `${API_BASE}/api/v1/issues/${id}`,

  overview: () => `${API_BASE}/api/v1/analytics/overview`,
  volumeSeries: (params: string) => `${API_BASE}/api/v1/analytics/volume-series?${params}`,

  triggerSimulation: () => `${API_BASE}/api/v1/simulation/trigger`,
  simulationStatus: () => `${API_BASE}/api/v1/simulation/status`,
  stopSimulation: (scenario: string) => `${API_BASE}/api/v1/simulation/stop/${scenario}`,
  listScenarios: () => `${API_BASE}/api/v1/simulation/scenarios`,

  ask: () => `${API_BASE}/api/v1/ask`,

  ws: () => `${WS_BASE}/api/v1/ws`,
};

// --- Mock Data Fallbacks for Standalone Frontend Demo ---

const MOCK_OVERVIEW = {
  total_tickets: 8420,
  active_issues: 3,
  critical_issues: 1,
  avg_sentiment: -0.24,
  tickets_today: 342,
  tickets_this_hour: 48,
  top_categories: [
    { category: 'payments', count: 2450 },
    { category: 'login', count: 2100 },
    { category: 'mobile_app', count: 1650 },
    { category: 'delivery', count: 1220 },
    { category: 'subscriptions', count: 1000 },
  ],
  sentiment_distribution: {
    negative: 3200,
    neutral: 4100,
    positive: 1120,
  },
};

const generateMockVolumeSeries = () => {
  const points = [];
  const now = new Date();
  for (let i = 24; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 3600 * 1000);
    const hour = t.getHours();
    const isSpike = i >= 2 && i <= 6;
    const baseline = Math.round(15 + Math.sin(hour / 3) * 10);
    const volume = isSpike ? baseline + Math.round(45 + Math.random() * 20) : Math.max(5, baseline + Math.round((Math.random() - 0.5) * 8));

    points.push({
      timestamp: t.toISOString(),
      volume,
      baseline,
    });
  }
  return { series: points, interval: '1h' };
};

let MOCK_ISSUES = [
  {
    id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    title: 'Visa Card Payment Gateway Outage',
    summary: 'High-density semantic cluster of 87 support tickets reporting recurring 402 Payment Required errors when selecting Visa at checkout.',
    severity: 'CRITICAL',
    status: 'DETECTED',
    confidence_score: 0.96,
    ticket_count: 87,
    volume_growth_pct: 340,
    sentiment_avg: -0.68,
    first_detected_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    key_terms: ['Visa', 'checkout error', '402 error'],
  },
  {
    id: 'a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6',
    title: 'Android 14 Crash on App Launch (v5.2.0)',
    summary: 'Spike in mobile app crash logs immediately following v5.2.0 update on Android 14 devices.',
    severity: 'HIGH',
    status: 'INVESTIGATING',
    confidence_score: 0.89,
    ticket_count: 42,
    volume_growth_pct: 180,
    sentiment_avg: -0.52,
    first_detected_at: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
    key_terms: ['Android 14', 'app crash', 'v5.2.0'],
  },
  {
    id: 'b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7',
    title: 'EU Regional Delivery Delays & Tracking Timeouts',
    summary: 'Carrier tracking API timeouts causing customer support inquiries regarding package status in Germany & UK.',
    severity: 'MEDIUM',
    status: 'MITIGATED',
    confidence_score: 0.78,
    ticket_count: 29,
    volume_growth_pct: 85,
    sentiment_avg: -0.31,
    first_detected_at: new Date(Date.now() - 360 * 60 * 1000).toISOString(),
    key_terms: ['EU delivery', 'tracking timeout', 'carrier delay'],
  },
];

const MOCK_DETAILS: Record<string, unknown> = {
  'f47ac10b-58cc-4372-a567-0e02b2c3d479': {
    issue: {
      id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
      title: 'Visa Card Payment Gateway Outage',
      summary: 'High-density semantic cluster of 87 support tickets reporting recurring 402 Payment Required errors specifically when selecting Visa credit/debit cards at checkout. MasterCard and PayPal transactions remain unaffected.',
      severity: 'CRITICAL',
      status: 'DETECTED',
      confidence_score: 0.96,
      ticket_count: 87,
      volume_growth_pct: 340,
      sentiment_avg: -0.68,
      first_detected_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
      last_updated_at: new Date().toISOString(),
      affected_demographics: {
        countries: { US: 42, GB: 18, DE: 12, FR: 8, CA: 7 },
        devices: { 'Web-Chrome': 45, iOS: 22, Android: 14, 'Web-Safari': 6 },
        plans: { Pro: 48, Enterprise: 26, Free: 13 },
      },
      key_terms: ['Visa', 'checkout error', 'payment declined', 'card rejected', '402 error'],
      root_cause_hypothesis: 'Recent payment gateway SDK update (v4.1.2) misconfigures 3D-Secure authentication handshake for Visa card BIN ranges.',
      why_detected_breakdown: {
        volume_spike: 'Ticket rate jumped from 4.2/hr baseline to 48/hr (+340% volume spike).',
        semantic_cohesion: 'Cosine similarity between ticket vector embeddings averaged 0.88, indicating identical core problem.',
        sentiment_drop: 'Average cluster sentiment dropped to -0.68 (vs baseline -0.15).',
      },
    },
    timeline: [
      {
        id: '1',
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        event_type: 'SEVERITY_ESCALATED',
        title: 'Incident Detected & Escalated to CRITICAL',
        description: 'Z-score anomaly threshold exceeded (3.4σ above baseline). Auto-generated incident alert broadcast to Slack #incidents.',
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        event_type: 'CLUSTER_GROWTH',
        title: 'Cluster Expanded to 50+ Tickets',
        description: 'Semantic vector centroid shifted towards 3D-Secure timeout errors.',
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        event_type: 'ROOT_CAUSE_GENERATED',
        title: 'AI Root Cause Hypothesis Generated',
        description: 'Correlated failure pattern identified in PaymentGateway SDK v4.1.2.',
      },
    ],
    sample_tickets: [
      {
        ticket_id: 'TK-SIM-9A4B',
        message: 'My Visa card payment keeps getting declined at the final step of checkout.',
        category: 'payments',
        priority: 'urgent',
        channel: 'web_form',
        country: 'US',
        platform_device: 'Web-Chrome',
        customer_plan: 'Enterprise',
        sentiment_score: -0.72,
        created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        similarity_score: 0.94,
      },
      {
        ticket_id: 'TK-SIM-7C2D',
        message: 'Getting error code 402 when paying with Visa. MasterCard works fine though.',
        category: 'payments',
        priority: 'high',
        channel: 'chat',
        country: 'GB',
        platform_device: 'iOS',
        customer_plan: 'Pro',
        sentiment_score: -0.65,
        created_at: new Date(Date.now() - 18 * 60 * 1000).toISOString(),
        similarity_score: 0.91,
      },
      {
        ticket_id: 'TK-SIM-3E8F',
        message: 'Payment failure with Visa card. Tried 3 times already today.',
        category: 'payments',
        priority: 'urgent',
        channel: 'email',
        country: 'US',
        platform_device: 'Web-Chrome',
        customer_plan: 'Enterprise',
        sentiment_score: -0.81,
        created_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
        similarity_score: 0.89,
      },
      {
        ticket_id: 'TK-SIM-1F5A',
        message: 'Checkout rejects my Visa card every time I try to complete order.',
        category: 'payments',
        priority: 'high',
        channel: 'mobile_app',
        country: 'DE',
        platform_device: 'Android',
        customer_plan: 'Pro',
        sentiment_score: -0.58,
        created_at: new Date(Date.now() - 32 * 60 * 1000).toISOString(),
        similarity_score: 0.86,
      },
    ],
  },
};

export async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 1200);

  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    clearTimeout(timeoutId);

    // Fallback logic for demo when backend server is offline or times out
    if (url.includes('/analytics/overview')) {
      return MOCK_OVERVIEW as unknown as T;
    }
    if (url.includes('/analytics/volume-series')) {
      return generateMockVolumeSeries() as unknown as T;
    }
    if (url.includes('/issues/')) {
      const issueId = url.split('/issues/')[1]?.split('?')[0];
      if (issueId && MOCK_DETAILS[issueId]) {
        return MOCK_DETAILS[issueId] as unknown as T;
      }
      return MOCK_DETAILS['f47ac10b-58cc-4372-a567-0e02b2c3d479'] as unknown as T;
    }
    if (url.includes('/issues')) {
      let issues = [...MOCK_ISSUES];
      if (url.includes('status=')) {
        const statusParam = url.split('status=')[1]?.split('&')[0];
        if (statusParam && statusParam.toLowerCase() !== 'all') {
          issues = issues.filter((i) => i.status.toUpperCase() === statusParam.toUpperCase());
        }
      }
      return { issues, total: issues.length } as unknown as T;
    }
    if (url.includes('/simulation/trigger')) {
      return { status: 'STARTED', scenario: 'visa_outage', speed: 5, ticket_count: 150 } as unknown as T;
    }
    if (url.includes('/simulation/status')) {
      return { simulations: {}, any_running: false } as unknown as T;
    }
    if (url.includes('/simulation/scenarios')) {
      return {
        scenarios: [
          { id: 'visa_outage', label: 'Visa Outage', category: 'payments' },
          { id: 'login_bug', label: 'Login Bug', category: 'login' },
          { id: 'mobile_crash', label: 'Mobile Crash', category: 'mobile_app' },
          { id: 'delivery_delay', label: 'Delivery Delay', category: 'delivery' },
          { id: 'subscription_issue', label: 'Subscription Issue', category: 'subscriptions' },
        ],
      } as unknown as T;
    }

    if (url.includes('/ask')) {
      let q = '';
      try {
        if (options?.body) {
          const parsed = JSON.parse(options.body as string);
          q = parsed.question || '';
        }
      } catch (e) {}
      return {
        question: q,
        answer: `Vector search completed for '${q || 'query'}': Analyzing 8,420 support tickets. Primary anomaly cluster is concentrated in payment gateway Visa 402 errors (+340% volume spike).`,
        sources_count: 12
      } as unknown as T;
    }

    throw err;
  }
}
