import { render, screen } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }));
});

test('renders the sentiment dashboard heading', () => {
  render(<App />);
  expect(screen.getByText(/maandamano sentiment dashboard/i)).toBeInTheDocument();
});
