import { useCallback, useEffect, useState } from 'react';
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
  const [status, setStatus] = useState('Connecting to monitoring API…');
  const [source, setSource] = useState('mock');
  const [activePage, setActivePage] = useState('dashboard');

  const loadDashboard = useCallback(async () => {
    try {
      const paths = ['dashboard/summary', 'dashboard/trends', 'dashboard/geographic', 'dashboard/keywords', 'dashboard/escalation', 'posts'];
      const results = await Promise.all(paths.map(async path => {
        const response = await fetch(`${API}/${path}`);
        if (!response.ok) throw new Error(`${path}: ${response.status}`);
        return response.json();
      }));
      setSummary(results[0]); setTrends(results[1]); setLocations(results[2]);
      setKeywords(results[3]); setAlert(results[4]); setPosts(results[5]);
      setStatus(results[0].total_posts ? `${results[0].total_posts} records loaded from the API` : 'No records collected yet');
    } catch (error) {
      setStatus(`API unavailable — ${error.message}`);
    }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  const collectData = async () => {
    const isDemo = source === 'mock';
    setStatus(isDemo ? 'Generating demo records…' : `Collecting recent ${source} posts…`);
    try {
      const response = await fetch(`${API}/collect`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source, count: 50 }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Collection request failed');
      await loadDashboard();
      setStatus(`${payload.stored} new ${isDemo ? 'demo' : source} records added`);
    } catch (error) { setStatus(error.message); }
  };

  const clearData = async () => {
    if (!window.confirm('Clear all locally collected dashboard data?')) return;
    setStatus('Clearing local data…');
    try {
      const response = await fetch(`${API}/posts`, { method: 'DELETE' });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Could not clear data');
      await loadDashboard();
      setStatus(payload.message);
    } catch (error) { setStatus(error.message); }
  };

  const latestTrend = trends[trends.length - 1];
  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand-lockup"><div className="flag-mark" aria-hidden="true"><i /><i /><i /></div><div><p className="eyebrow">Sentiment analysis project · Kenya</p><h1>Maandamano <em>Sentiment Tracker</em></h1><p className="subtitle">A simple dashboard for following public discussions around protests and cost of living.</p></div></div>
        <div className="controls"><span className="api-status"><i />{status}</span><div className="button-group"><select value={source} onChange={event => setSource(event.target.value)} aria-label="Data source"><option value="mock">Demo data</option><option value="reddit">Reddit</option><option value="twitter">X / Twitter</option></select><button onClick={collectData}>Collect data</button><button className="secondary" onClick={loadDashboard}>Refresh</button><button className="clear" onClick={clearData}>Clear</button></div></div>
      </header>

      <nav className="main-nav" aria-label="Main navigation">
        <button className={activePage === 'dashboard' ? 'active' : ''} onClick={() => setActivePage('dashboard')}>Dashboard</button>
        <button className={activePage === 'collection' ? 'active' : ''} onClick={() => setActivePage('collection')}>Data collection</button>
        <button className={activePage === 'reports' ? 'active' : ''} onClick={() => setActivePage('reports')}>Reports</button>
      </nav>

      {activePage === 'dashboard' && <>
      <section className="context-bar"><span><b>Project focus:</b> Kenya · public online posts</span><span><b>Current data:</b> {summary.total_posts ? 'API records' : 'Awaiting collection'}</span><span><b>Method:</b> basic sentiment classification</span></section>

      <section className="metrics" aria-label="Sentiment summary">
        <Metric label="Posts analysed" value={summary.total_posts} tone="black" />
        <Metric label="Positive" value={`${summary.positive_pct}%`} tone="green" />
        <Metric label="Neutral" value={`${summary.neutral_pct}%`} tone="gray" />
        <Metric label="Negative" value={`${summary.negative_pct}%`} tone="red" />
      </section>

      <section className="content-grid">
        <article className="panel wide"><div className="panel-heading"><div><p className="section-kicker">What people are saying</p><h2>Sentiment trend</h2></div><span className="legend"><i className="positive" /> Positive <i className="neutral" /> Neutral <i className="negative" /> Negative</span></div><p className="muted">Percentage of posts in each sentiment category, grouped by date.</p>
          {trends.length ? <div className="trend-list">{trends.map(day => <div className="trend-row" key={day.date}><span>{day.date}</span><div className="stack"><i className="positive" style={{ width: `${day.positive}%` }} /><i className="neutral" style={{ width: `${day.neutral}%` }} /><i className="negative" style={{ width: `${day.negative}%` }} /></div><b>{day.negative}% negative</b></div>)}</div> : <Empty text="Collect data to view daily trends." />}
        </article>
        <article className={`panel alert ${alert.alert_level.toLowerCase()}`}><p className="section-kicker">Simple risk score</p><h2>Escalation signal</h2><div className="score">{alert.score}<small>/100</small></div><strong>{alert.alert_level}</strong><p className="muted">Calculated from negative posts, risk words, and changes in volume.</p><p className="muted">Last 24h: {alert.recent_posts || 0} · Prior 24h: {alert.prior_posts || 0}</p></article>
        <article className="panel"><p className="section-kicker">Geographic signal</p><h2>Locations</h2>{locations.length ? <div className="location-list">{locations.slice(0, 8).map(item => <div key={item.location}><span>{item.location}</span><b>{item.negative_pct}% negative</b><div className="bar"><i style={{ width: `${item.negative_pct}%` }} /></div></div>)}</div> : <Empty text="No reliable location data yet." />}</article>
        <article className="panel"><p className="section-kicker">Conversation themes</p><h2>Top discussion terms</h2>{keywords.length ? <div className="tags">{keywords.map(item => <span key={item.keyword}>{item.keyword} <b>{item.count}</b></span>)}</div> : <Empty text="Keywords will appear after collection." />}</article>
        <article className="panel wide"><div className="panel-heading"><div><p className="section-kicker">Source feed</p><h2>Recent posts</h2></div><span className="table-note">Latest API records</span></div><div className="table-wrap"><table><thead><tr><th>Time</th><th>Post</th><th>Language</th><th>Source</th><th>Sentiment</th><th>Confidence</th></tr></thead><tbody>{posts.slice(0, 12).map(post => <tr key={post.post_id}><td>{post.timestamp ? new Date(post.timestamp).toLocaleString() : '—'}</td><td>{post.content}</td><td>{post.language}</td><td>{post.platform}</td><td><span className={`pill ${post.sentiment_type}`}>{post.sentiment_type}</span></td><td>{Math.round(post.confidence_score * 100)}%</td></tr>)}</tbody></table>{!posts.length && <Empty text="Choose Demo data and click Collect data to populate this dashboard." />}</div></article>
      </section>
      </>}

      {activePage === 'collection' && <section className="page-view">
        <div className="page-heading"><p className="section-kicker">Step 1 · Get records</p><h2>Data collection</h2><p>Choose a source and collect posts for the dashboard. Demo data is included for testing without credentials.</p></div>
        <div className="collection-grid">
          <article className="panel collection-card"><p className="section-kicker">Quick start</p><h2>Demo dataset</h2><p className="muted">Adds sample Kenya-focused posts across Nairobi locations, languages, and sentiment categories.</p><button onClick={() => { setSource('mock'); collectData(); }}>Load 50 demo posts</button></article>
          <article className="panel collection-card"><p className="section-kicker">Live source</p><h2>Reddit collection</h2><p className="muted">Searches recent public Reddit content. Add your Reddit credentials in the backend <code>.env</code> file first.</p><button className="secondary" onClick={() => { setSource('reddit'); collectData(); }}>Collect from Reddit</button></article>
          <article className="panel collection-card"><p className="section-kicker">Data management</p><h2>Start over</h2><p className="muted">Remove records stored in this local project database before a new test run.</p><button className="clear" onClick={clearData}>Clear all data</button></article>
        </div>
        <article className="panel run-summary"><p className="section-kicker">Collection status</p><h2>{summary.total_posts} posts currently stored</h2><p className="muted">{status}</p><button className="secondary" onClick={loadDashboard}>Check for updates</button></article>
      </section>}

      {activePage === 'reports' && <section className="page-view">
        <div className="page-heading"><p className="section-kicker">Step 2 · Review results</p><h2>Analysis report</h2><p>A quick summary based on all records currently stored in the application.</p></div>
        <div className="report-grid">
          <article className="panel report-highlight"><p className="section-kicker">Overall result</p><h2>{summary.total_posts ? `${summary.negative_pct}% of posts are negative` : 'No results yet'}</h2><p className="muted">{summary.total_posts ? `Out of ${summary.total_posts} analysed posts, the current escalation score is ${alert.score}/100 (${alert.alert_level}).` : 'Collect demo data first to generate a report.'}</p></article>
          <article className="panel"><p className="section-kicker">Sentiment split</p><h2>Current percentages</h2><div className="report-list"><span>Positive <b>{summary.positive_pct}%</b></span><span>Neutral <b>{summary.neutral_pct}%</b></span><span>Negative <b>{summary.negative_pct}%</b></span></div></article>
          <article className="panel"><p className="section-kicker">Locations to review</p><h2>Highest negative share</h2>{locations.length ? <div className="report-list">{locations.slice(0, 4).map(location => <span key={location.location}>{location.location} <b>{location.negative_pct}%</b></span>)}</div> : <Empty text="Location results will appear after collection." />}</article>
          <article className="panel wide"><p className="section-kicker">Key themes</p><h2>Frequently used words</h2>{keywords.length ? <div className="tags">{keywords.map(item => <span key={item.keyword}>{item.keyword} <b>{item.count}</b></span>)}</div> : <Empty text="Keyword results will appear after collection." />}</article>
        </div>
      </section>}
      <footer>Maandamano Sentiment Tracker · Student project dashboard {latestTrend && `· Latest data: ${latestTrend.date}`}</footer>
    </main>
  );
}

function Metric({ label, value, tone }) { return <article className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong></article>; }
function Empty({ text }) { return <p className="empty">{text}</p>; }
export default App;
