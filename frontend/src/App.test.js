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
    if (url.includes('posts')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
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
