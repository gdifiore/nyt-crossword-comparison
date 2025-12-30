import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorageMock.clear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
  });

  describe('Initial Render', () => {
    test('renders title', () => {
      render(<App />);
      expect(screen.getByText(/nyt crossword comparison/i)).toBeInTheDocument();
    });

    test('shows time input when no time entered', () => {
      render(<App />);
      expect(screen.getByLabelText(/enter your time/i)).toBeInTheDocument();
    });

    test('uses getStoredTimeData helper to initialize state', () => {
      render(<App />);

      // Should call localStorage.getItem for each stored value
      expect(localStorageMock.getItem).toHaveBeenCalledWith('date');
      expect(localStorageMock.getItem).toHaveBeenCalledWith('timeEntered');
      expect(localStorageMock.getItem).toHaveBeenCalledWith('userTime');
    });
  });

  describe('State Management After Submission', () => {
    test('shows user time after submission', async () => {
      const today = new Date().toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return today;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] })
      });

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/your time: 1:23/i)).toBeInTheDocument();
      });
    });

    test('fetches chart data when time is entered', async () => {
      const today = new Date().toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return today;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: [
            { range: '1:00-1:30', count: 5 },
            { range: '1:30-2:00', count: 3 }
          ]
        })
      });

      render(<App />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/chartData', expect.any(Object));
      });
    });

    test('shows loading state while fetching chart data', async () => {
      const today = new Date().toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return today;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      fetch.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      render(<App />);

      expect(screen.getByText(/loading chart data/i)).toBeInTheDocument();
    });

    test('handles chart data fetch error', async () => {
      const today = new Date().toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return today;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load chart data/i)).toBeInTheDocument();
      });
    });
  });

  describe('AbortController Cleanup', () => {
    test('aborts fetch on component unmount', async () => {
      const today = new Date().toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return today;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      const abortSpy = jest.spyOn(AbortController.prototype, 'abort');

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] })
      });

      const { unmount } = render(<App />);

      unmount();

      expect(abortSpy).toHaveBeenCalled();
      abortSpy.mockRestore();
    });
  });

  describe('Date Handling', () => {
    test('resets time entered if date changed', () => {
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'date') return yesterday;
        if (key === 'timeEntered') return 'true';
        if (key === 'userTime') return '1:23';
        return null;
      });

      render(<App />);

      // Should show input form since date doesn't match
      expect(screen.getByLabelText(/enter your time/i)).toBeInTheDocument();
    });
  });
});
