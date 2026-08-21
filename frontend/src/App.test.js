import { render, screen, act } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  global.fetch = jest.fn((url) => {
    if (url.includes('summary')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ total_posts: 10, positive_pct: 30, negative_pct: 50, neutral_pct: 20 }),
      });
    }
    if (url.includes('trends')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.includes('geographic')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.includes('keywords')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.includes('escalation')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ score: 45, alert_level: 'Medium', recent_posts: 10, prior_posts: 5 }),
      });
    }
    if (url.includes('live')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          timestamp: new Date().toISOString(),
          status: 'streaming',
          total_posts: 10,
          posting_velocity_per_min: 2.5,
          sentiment_distribution: { positive: 3, neutral: 2, negative: 5, positive_pct: 30, neutral_pct: 20, negative_pct: 50 },
          escalation: { score: 45, alert_level: 'Medium' },
          stream: [
            { post_id: 1, content: 'Amani na haki nchini Kenya', language: 'swahili', platform: 'twitter', location: 'Nairobi CBD', sentiment_type: 'positive', confidence_score: 0.9, timestamp: new Date().toISOString() }
          ]
        }),
      });
    }
    if (url.includes('posts')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.includes('auth/me')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ user: { id: 1, username: 'analyst', role: 'Senior Analyst', email: 'analyst@maandamanopulse.co.ke' } }),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
});

afterEach(() => {
  jest.clearAllMocks();
});

test('renders Maandamano Pulse title and elements', async () => {
  await act(async () => {
    render(<App />);
  });
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/Maandamano Pulse/i);
  expect(screen.getByText(/Civic Tech Sentiment Engine/i)).toBeInTheDocument();
});

test('switches to Real-Time Data Stream and Log In tabs', async () => {
  await act(async () => {
    render(<App />);
  });

  const liveTab = screen.getByRole('button', { name: /Real-Time Data Stream/i });
  await act(async () => {
    liveTab.click();
  });
  expect(screen.getByText(/Real-Time Citizen Discussion Stream/i)).toBeInTheDocument();

  const loginTab = screen.getByRole('button', { name: /Log In Page/i });
  await act(async () => {
    loginTab.click();
  });
  expect(screen.getByRole('heading', { name: /Analyst Log In/i })).toBeInTheDocument();
});
