import { useCallback, useEffect, useState } from 'react';
import Login from './Login';
import './App.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const emptySummary = { total_posts: 0, positive_pct: 0, negative_pct: 0, neutral_pct: 0 };

function App() {
  const [summary, setSummary] = useState(emptySummary);
  const [trends, setTrends] = useState([]);
  const [locations, setLocations] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [posts, setPosts] = useState([]);
  const [alert, setAlert] = useState({ score: 0, alert_level: 'Low' });
  const [status, setStatus] = useState('Connecting to Maandamano Pulse API…');
  const [source, setSource] = useState('mock');
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedLanguage, setSelectedLanguage] = useState('all');

  // Authentication State
  const [currentUser, setCurrentUser] = useState(null);
  const [authToken, setAuthToken] = useState(localStorage.getItem('token') || '');

  // Real-time Data Stream State
  const [isLiveStreaming, setIsLiveStreaming] = useState(true);
  const [liveData, setLiveData] = useState(null);
  const [lastLiveSync, setLastLiveSync] = useState(null);

  // Validate session on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch(`${API}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.ok ? res.json() : Promise.reject())
        .then(data => {
          setCurrentUser(data.user);
          setAuthToken(token);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setCurrentUser(null);
          setAuthToken('');
        });
    }
  }, []);

  const loadDashboard = useCallback(async () => {
    try {
      const paths = ['dashboard/summary', 'dashboard/trends', 'dashboard/geographic', 'dashboard/keywords', 'dashboard/escalation', 'posts'];
      const results = await Promise.all(paths.map(async path => {
        const response = await fetch(`${API}/${path}`);
        if (!response.ok) throw new Error(`${path}: ${response.status}`);
        return response.json();
      }));
      setSummary(results[0]);
      setTrends(results[1]);
      setLocations(results[2]);
      setKeywords(results[3]);
      setAlert(results[4]);
      setPosts(results[5]);
      setStatus(results[0].total_posts ? `${results[0].total_posts} live entries synced from backend` : 'Ready to collect live Kenyan online feeds');
    } catch (error) {
      setStatus(`Backend Offline (${error.message}) — start Flask server on port 5000`);
    }
  }, []);

  const fetchLiveData = useCallback(async () => {
    try {
      const res = await fetch(`${API}/dashboard/live`);
      if (res.ok) {
        const data = await res.json();
        setLiveData(data);
        setLastLiveSync(new Date().toLocaleTimeString());
      }
    } catch (err) {
      console.error('Real-time sync error:', err);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
    fetchLiveData();
  }, [loadDashboard, fetchLiveData]);

  // Real-time auto-polling interval
  useEffect(() => {
    let intervalId;
    if (isLiveStreaming) {
      intervalId = setInterval(() => {
        fetchLiveData();
        loadDashboard();
      }, 3000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isLiveStreaming, fetchLiveData, loadDashboard]);

  const handleLoginSuccess = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    setActivePage('dashboard');
  };

  const handleLogout = async () => {
    if (authToken) {
      fetch(`${API}/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
      }).catch(() => {});
    }
    localStorage.removeItem('token');
    setCurrentUser(null);
    setAuthToken('');
  };

  const collectData = async () => {
    const isDemo = source === 'mock';
    setStatus(isDemo ? 'Generating authentic Kenyan social media entries…' : `Fetching recent ${source} discussions…`);
    try {
      const response = await fetch(`${API}/collect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, count: 50 })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Data collection failed');
      await loadDashboard();
      await fetchLiveData();
      setStatus(`Successfully fetched ${payload.stored} new records from ${isDemo ? 'Kenyan Demo Stream' : source}`);
    } catch (error) { setStatus(`Collection failed: ${error.message}`); }
  };

  const clearData = async () => {
    if (!window.confirm('Clear all collected posts and reset the dashboard?')) return;
    setStatus('Clearing stored sentiment records…');
    try {
      const response = await fetch(`${API}/posts`, { method: 'DELETE' });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Failed to clear data');
      await loadDashboard();
      await fetchLiveData();
      setStatus(payload.message || 'Dashboard cleared.');
    } catch (error) { setStatus(error.message); }
  };

  const filteredPosts = posts.filter(post => selectedLanguage === 'all' || post.language === selectedLanguage);
  const latestTrend = trends[trends.length - 1];

  return (
    <div className="app-container">
      {/* Decorative Maasai / Kenyan Cultural Header Banner */}
      <div className="cultural-header-bar" aria-hidden="true">
        <div className="beadwork-pattern"></div>
      </div>

      <main className="dashboard">
        <header className="topbar">
          <div className="brand-lockup">
            <div className="kenya-shield-badge" title="Kenya Citizen Pulse">
              <span className="badge-flag-strip black"></span>
              <span className="badge-flag-strip red"></span>
              <span className="badge-flag-strip green"></span>
            </div>
            <div>
              <div className="badge-row">
                <span className="kenya-pill"><span className="flag-dot"></span> KENYA</span>
                <span className="project-tag">Civic Tech Sentiment Engine</span>
              </div>
              <h1>Maandamano <em>Pulse</em></h1>
              <p className="subtitle">Real-time public sentiment, Sheng/Swahili language monitoring & tension alert system for Kenyan protests.</p>
            </div>
          </div>

          <div className="controls">
            <div className="user-profile-badge">
              {currentUser ? (
                <div className="user-info">
                  <span className="user-icon">👤</span>
                  <div className="user-meta">
                    <strong>{currentUser.username}</strong>
                    <small>{currentUser.role}</small>
                  </div>
                  <button className="logout-btn" onClick={handleLogout} title="Log Out">Logout</button>
                </div>
              ) : (
                <button className="login-header-btn" onClick={() => setActivePage('login')}>
                  🔑 Analyst Log In
                </button>
              )}
            </div>

            <div className="api-status">
              <span className={isLiveStreaming ? "pulse-indicator active" : "pulse-indicator"}></span>
              <span className="status-text">{status}</span>
            </div>

            <div className="button-group">
              <select value={source} onChange={event => setSource(event.target.value)} aria-label="Select Feed Source">
                <option value="mock">🇰🇪 Kenyan Synthetic Feed (Demo)</option>
                <option value="reddit">Reddit (r/Kenya & Public)</option>
                <option value="twitter">X / Twitter API v2</option>
              </select>
              <button className="primary-btn" onClick={collectData}>📥 Fetch Feed</button>
              <button className="secondary-btn" onClick={loadDashboard}>🔄 Sync</button>
              <button className="clear-btn" onClick={clearData}>🗑️ Reset</button>
            </div>
          </div>
        </header>

        <nav className="main-nav" aria-label="Primary Navigation">
          <button className={activePage === 'dashboard' ? 'nav-tab active' : 'nav-tab'} onClick={() => setActivePage('dashboard')}>
            📊 Sentiment Overview
          </button>
          <button className={activePage === 'live' ? 'nav-tab active live-tab' : 'nav-tab live-tab'} onClick={() => setActivePage('live')}>
            ⚡ Real-Time Data Stream {isLiveStreaming && <span className="live-dot-ticker">🔴 LIVE</span>}
          </button>
          <button className={activePage === 'collection' ? 'nav-tab active' : 'nav-tab'} onClick={() => setActivePage('collection')}>
            📡 Data Feeds & Ingestion
          </button>
          <button className={activePage === 'reports' ? 'nav-tab active' : 'nav-tab'} onClick={() => setActivePage('reports')}>
            📝 NLP Analytics & Report
          </button>
          <button className={activePage === 'login' ? 'nav-tab active' : 'nav-tab'} onClick={() => setActivePage('login')}>
            🔑 {currentUser ? 'Account Profile' : 'Log In Page'}
          </button>
        </nav>

        {activePage === 'dashboard' && (
          <>
            <section className="context-bar">
              <span><b>Target Domain:</b> Kenya Protests, Finance Bill & Cost of Living</span>
              <span><b>Linguistic Scope:</b> English, Swahili & Sheng Code-switching</span>
              <span><b>Model:</b> XLM-RoBERTa + Sheng Lexicon Alignment</span>
            </section>

            <section className="metrics" aria-label="Sentiment Summary Cards">
              <Metric label="Total Posts Monitored" value={summary.total_posts} tone="black" icon="💬" />
              <Metric label="Positive Sentiment" value={`${summary.positive_pct}%`} tone="green" icon="🕊️" />
              <Metric label="Neutral Discussion" value={`${summary.neutral_pct}%`} tone="gray" icon="⚖️" />
              <Metric label="Negative / Tension" value={`${summary.negative_pct}%`} tone="red" icon="🔥" />
            </section>

            <section className="content-grid">
              <article className="panel wide">
                <div className="panel-heading">
                  <div>
                    <p className="section-kicker">Temporal Sentiment Trend</p>
                    <h2>Daily Citizen Sentiment Distribution</h2>
                  </div>
                  <span className="legend">
                    <i className="positive" /> Positive <i className="neutral" /> Neutral <i className="negative" /> Tension
                  </span>
                </div>
                <p className="muted">Proportion of positive, neutral, and tense posts aggregated by date.</p>
                {trends.length ? (
                  <div className="trend-list">
                    {trends.map(day => (
                      <div className="trend-row" key={day.date}>
                        <span className="trend-date">{day.date}</span>
                        <div className="stack">
                          <i className="positive" style={{ width: `${day.positive}%` }} title={`Positive: ${day.positive}%`} />
                          <i className="neutral" style={{ width: `${day.neutral}%` }} title={`Neutral: ${day.neutral}%`} />
                          <i className="negative" style={{ width: `${day.negative}%` }} title={`Negative: ${day.negative}%`} />
                        </div>
                        <b className="trend-stat">{day.negative}% tense</b>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Empty text="Click 'Fetch Feed' above to populate sentiment trends." />
                )}
              </article>

              <article className={`panel alert ${alert.alert_level ? alert.alert_level.toLowerCase() : 'low'}`}>
                <p className="section-kicker">Real-time Safety Alert</p>
                <h2>Escalation Risk Signal</h2>
                <div className="score">
                  {alert.score}
                  <small>/100</small>
                </div>
                <div className="alert-badge-wrap">
                  <span className={`alert-badge ${alert.alert_level ? alert.alert_level.toLowerCase() : 'low'}`}>
                    {alert.alert_level || 'Low'} Risk Level
                  </span>
                </div>
                <p className="muted">Evaluates negative sentiment density, risk keywords (e.g. tear gas, arrests), and post volume surge.</p>
                <div className="window-stats">
                  <span>Last 24h: <b>{alert.recent_posts || 0} posts</b></span>
                  <span>Prior 24h: <b>{alert.prior_posts || 0} posts</b></span>
                </div>
              </article>

              <article className="panel">
                <p className="section-kicker">Regional Sentiment</p>
                <h2>Kenyan Hotspots</h2>
                {locations.length ? (
                  <div className="location-list">
                    {locations.slice(0, 8).map(item => (
                      <div key={item.location} className="location-item">
                        <div className="location-header">
                          <span className="loc-name">📍 {item.location}</span>
                          <b className="loc-neg">{item.negative_pct}% negative</b>
                        </div>
                        <div className="bar">
                          <i style={{ width: `${item.negative_pct}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Empty text="Location breakdown will appear after fetching posts." />
                )}
              </article>

              <article className="panel">
                <p className="section-kicker">Linguistic & Key Terms</p>
                <h2>Top Discussion Topics</h2>
                {keywords.length ? (
                  <div className="tags">
                    {keywords.map(item => (
                      <span key={item.keyword} className="tag-chip">
                        #{item.keyword} <b className="tag-count">{item.count}</b>
                      </span>
                    ))}
                  </div>
                ) : (
                  <Empty text="Top keywords will appear once posts are collected." />
                )}
              </article>

              <article className="panel wide">
                <div className="panel-heading">
                  <div>
                    <p className="section-kicker">Social Stream Analysis</p>
                    <h2>Live Posts Feed & NLP Output</h2>
                  </div>
                  <div className="filter-wrap">
                    <label htmlFor="lang-filter">Filter Language: </label>
                    <select id="lang-filter" value={selectedLanguage} onChange={e => setSelectedLanguage(e.target.value)}>
                      <option value="all">All Languages</option>
                      <option value="sheng">Sheng</option>
                      <option value="swahili">Swahili</option>
                      <option value="english">English</option>
                    </select>
                  </div>
                </div>

                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Content</th>
                        <th>Language</th>
                        <th>Platform</th>
                        <th>Location</th>
                        <th>Sentiment</th>
                        <th>Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPosts.slice(0, 15).map(post => (
                        <tr key={post.post_id}>
                          <td className="time-col">{post.timestamp ? new Date(post.timestamp).toLocaleString() : '—'}</td>
                          <td className="content-col">{post.content}</td>
                          <td><span className={`lang-badge ${post.language}`}>{post.language}</span></td>
                          <td><span className="platform-tag">{post.platform}</span></td>
                          <td>{post.location || 'Nairobi CBD'}</td>
                          <td><span className={`pill ${post.sentiment_type}`}>{post.sentiment_type}</span></td>
                          <td className="conf-col">{Math.round((post.confidence_score || 0) * 100)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {!filteredPosts.length && <Empty text="No matching posts found. Fetch feeds or select 'All Languages'." />}
                </div>
              </article>
            </section>
          </>
        )}

        {activePage === 'live' && (
          <section className="page-view">
            <div className="live-stream-header">
              <div>
                <p className="section-kicker">Live Analytics & Stream Presentation</p>
                <h2>Real-Time Citizen Discussion Stream</h2>
                <p className="muted">Continuous auto-polling updates tracking sentiment shifts and post velocity across Kenyan social channels.</p>
              </div>
              <div className="live-controls">
                <div className="live-status-pill">
                  <span className={isLiveStreaming ? "beacon active" : "beacon paused"}></span>
                  <strong>{isLiveStreaming ? "STREAMING LIVE (3s sync)" : "STREAM PAUSED"}</strong>
                </div>
                <button
                  className={isLiveStreaming ? "secondary-btn" : "primary-btn"}
                  onClick={() => setIsLiveStreaming(!isLiveStreaming)}
                >
                  {isLiveStreaming ? "⏸ Pause Live Stream" : "▶️ Resume Live Stream"}
                </button>
                {lastLiveSync && <small className="last-sync-tag">Last sync: {lastLiveSync}</small>}
              </div>
            </div>

            <section className="metrics live-metrics" aria-label="Real-Time Ticker Metrics">
              <article className="metric black">
                <div className="metric-header">
                  <span>Posting Velocity Rate</span>
                  <span className="metric-icon">⚡</span>
                </div>
                <strong>{liveData ? `${liveData.posting_velocity_per_min} posts/min` : '0.0 posts/min'}</strong>
              </article>

              <article className="metric red">
                <div className="metric-header">
                  <span>Live Escalation Risk</span>
                  <span className="metric-icon">🚨</span>
                </div>
                <strong>{liveData?.escalation ? `${liveData.escalation.score}/100 (${liveData.escalation.alert_level})` : '0/100'}</strong>
              </article>

              <article className="metric green">
                <div className="metric-header">
                  <span>Live Positive Share</span>
                  <span className="metric-icon">🕊️</span>
                </div>
                <strong>{liveData?.sentiment_distribution ? `${liveData.sentiment_distribution.positive_pct}%` : '0%'}</strong>
              </article>

              <article className="metric gray">
                <div className="metric-header">
                  <span>Total Ingested Volume</span>
                  <span className="metric-icon">📡</span>
                </div>
                <strong>{liveData ? `${liveData.total_posts} entries` : '0 entries'}</strong>
              </article>
            </section>

            <article className="panel wide live-feed-panel">
              <div className="panel-heading">
                <div>
                  <p className="section-kicker">Incoming Real-Time Feed</p>
                  <h2>Live Post Ingestion Activity</h2>
                </div>
                <span className="live-sync-indicator">Auto-refresh active</span>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Social Content</th>
                      <th>Dialect / Lang</th>
                      <th>Platform</th>
                      <th>Location</th>
                      <th>Sentiment Output</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {liveData?.stream?.map((post) => (
                      <tr key={post.post_id} className="live-row">
                        <td className="time-col">{new Date(post.timestamp).toLocaleTimeString()}</td>
                        <td className="content-col"><strong>{post.content}</strong></td>
                        <td><span className={`lang-badge ${post.language}`}>{post.language}</span></td>
                        <td><span className="platform-tag">{post.platform}</span></td>
                        <td>📍 {post.location}</td>
                        <td><span className={`pill ${post.sentiment_type}`}>{post.sentiment_type}</span></td>
                        <td className="conf-col">{Math.round((post.confidence_score || 0) * 100)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {(!liveData?.stream || liveData.stream.length === 0) && (
                  <Empty text="No live stream data. Click 'Fetch Feed' in the header to generate social posts." />
                )}
              </div>
            </article>
          </section>
        )}

        {activePage === 'collection' && (
          <section className="page-view">
            <div className="page-heading">
              <p className="section-kicker">Data Pipeline Control</p>
              <h2>Social Media Ingestion & Data Sources</h2>
              <p>Collect public discussions across platforms to run NLP classification and escalation detection.</p>
            </div>
            <div className="collection-grid">
              <article className="panel collection-card">
                <p className="section-kicker">Instant Synthetic Feed</p>
                <h2>Kenyan Social Stream (Demo)</h2>
                <p className="muted">Simulates real-time English, Swahili, and Sheng posts across Kenyan urban centers like Nairobi CBD, Kibra, Githurai, Kondele, Eldoret & Mombasa.</p>
                <button className="primary-btn" onClick={() => { setSource('mock'); collectData(); }}>⚡ Load 50 Kenyan Posts</button>
              </article>
              <article className="panel collection-card">
                <p className="section-kicker">Live Reddit Search</p>
                <h2>Reddit Ingestion</h2>
                <p className="muted">Searches public discussions in subreddits like r/Kenya. Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET configured in backend environment.</p>
                <button className="secondary-btn" onClick={() => { setSource('reddit'); collectData(); }}>Fetch from Reddit API</button>
              </article>
              <article className="panel collection-card">
                <p className="section-kicker">Live X / Twitter Search</p>
                <h2>X (Twitter) Ingestion</h2>
                <p className="muted">Polls recent tweets matching protest & civic keywords in Kenya. Requires TWITTER_BEARER_TOKEN in backend environment.</p>
                <button className="secondary-btn" onClick={() => { setSource('twitter'); collectData(); }}>Fetch from X API</button>
              </article>
            </div>
            <article className="panel run-summary">
              <p className="section-kicker">Ingestion Status</p>
              <h2>{summary.total_posts} records currently stored in SQLite database</h2>
              <p className="muted">{status}</p>
            </article>
          </section>
        )}

        {activePage === 'reports' && (
          <section className="page-view">
            <div className="page-heading">
              <p className="section-kicker">NLP Insights & Summary</p>
              <h2>Sentiment & Escalation Executive Report</h2>
              <p>Key findings and metrics generated from current stored records.</p>
            </div>
            <div className="report-grid">
              <article className="panel report-highlight">
                <p className="section-kicker">Overall Sentiment Breakdown</p>
                <h2>{summary.total_posts ? `${summary.negative_pct}% Tension / Negative Sentiment` : 'No data collected'}</h2>
                <p className="muted">
                  {summary.total_posts
                    ? `Analyzed ${summary.total_posts} citizen posts. Escalation score is calculated at ${alert.score}/100 (${alert.alert_level} Risk).`
                    : 'Fetch social feeds to build the sentiment report.'}
                </p>
              </article>
              <article className="panel">
                <p className="section-kicker">Sentiment Breakdown</p>
                <h2>Category Distribution</h2>
                <div className="report-list">
                  <span>Positive Sentiment <b>{summary.positive_pct}%</b></span>
                  <span>Neutral Discussion <b>{summary.neutral_pct}%</b></span>
                  <span>Tension / Negative <b>{summary.negative_pct}%</b></span>
                </div>
              </article>
              <article className="panel">
                <p className="section-kicker">High Risk Locations</p>
                <h2>Top Locations with Tension</h2>
                {locations.length ? (
                  <div className="report-list">
                    {locations.slice(0, 5).map(loc => (
                      <span key={loc.location}>{loc.location} <b>{loc.negative_pct}% tension</b></span>
                    ))}
                  </div>
                ) : (
                  <Empty text="Location results will appear after feed ingestion." />
                )}
              </article>
              <article className="panel wide">
                <p className="section-kicker">Dominant Keywords</p>
                <h2>Top Extracted Terms</h2>
                {keywords.length ? (
                  <div className="tags">
                    {keywords.map(item => (
                      <span key={item.keyword} className="tag-chip">
                        #{item.keyword} <b>{item.count}</b>
                      </span>
                    ))}
                  </div>
                ) : (
                  <Empty text="Keyword data will populate after ingestion." />
                )}
              </article>
            </div>
          </section>
        )}

        {activePage === 'login' && (
          <section className="page-view">
            <Login onLoginSuccess={handleLoginSuccess} currentUser={currentUser} />
          </section>
        )}

        <footer className="footer">
          <div className="footer-content">
            <span><b>Maandamano Pulse</b> · Kenyan Social Sentiment & Tension Analytics System</span>
            {latestTrend && <span className="footer-date">Latest Sync: {latestTrend.date}</span>}
          </div>
        </footer>
      </main>
    </div>
  );
}

function Metric({ label, value, tone, icon }) {
  return (
    <article className={`metric ${tone}`}>
      <div className="metric-header">
        <span>{label}</span>
        <span className="metric-icon">{icon}</span>
      </div>
      <strong>{value}</strong>
    </article>
  );
}

function Empty({ text }) {
  return <p className="empty">{text}</p>;
}

export default App;
