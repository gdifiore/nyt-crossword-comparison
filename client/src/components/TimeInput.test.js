import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TimeInput from './TimeInput';

// Mock fetch
global.fetch = jest.fn();

describe('TimeInput Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('Input Validation', () => {
    test('renders input field and submit button', () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      expect(screen.getByLabelText(/enter your time/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });

    test('accepts valid time format m:ss', () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      fireEvent.change(input, { target: { value: '1:23' } });

      expect(input.value).toBe('1:23');
      expect(screen.getByRole('button', { name: /submit/i })).not.toBeDisabled();
    });

    test('accepts valid time format mm:ss', () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      fireEvent.change(input, { target: { value: '12:34' } });

      expect(input.value).toBe('12:34');
      expect(screen.getByRole('button', { name: /submit/i })).not.toBeDisabled();
    });

    test('disables submit button when input is empty', () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();
    });

    test('disables submit button for invalid format', () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      fireEvent.change(input, { target: { value: '123' } });

      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();
    });

    test('shows error for 0:00', async () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '0:00' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid time/i)).toBeInTheDocument();
      });
    });

    test('shows error for time over 15:00', async () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '16:00' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/too slow/i)).toBeInTheDocument();
      });
    });

    test('shows error for time under 0:10', async () => {
      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '0:05' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/too fast/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.runOnlyPendingTimers();
      jest.useRealTimers();
    });

    test('submits valid time successfully and shows success message', async () => {
      const mockOnTimeInput = jest.fn();
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Success' })
      });

      render(<TimeInput onTimeInput={mockOnTimeInput} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ secondsToComplete: 83 })
        });
        expect(screen.getByText(/time submitted successfully/i)).toBeInTheDocument();
      });

      // Fast-forward past the success message delay
      jest.advanceTimersByTime(800);

      await waitFor(() => {
        expect(mockOnTimeInput).toHaveBeenCalledWith(83);
      });
    });

    test('shows loading state during submission', async () => {
      fetch.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.click(submitButton);

      expect(screen.getByText(/submitting/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    test('handles server error', async () => {
      const mockOnError = jest.fn();
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Server error' })
      });

      render(<TimeInput onTimeInput={jest.fn()} onError={mockOnError} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/server error/i)).toBeInTheDocument();
        expect(mockOnError).toHaveBeenCalled();
      });
    });

    test('handles network error', async () => {
      const mockOnError = jest.fn();
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<TimeInput onTimeInput={jest.fn()} onError={mockOnError} />);

      const input = screen.getByLabelText(/enter your time/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
        expect(mockOnError).toHaveBeenCalled();
      });
    });
  });

  describe('Enter Key Support', () => {
    test('submits form when Enter is pressed', async () => {
      const mockOnTimeInput = jest.fn();
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Success' })
      });

      render(<TimeInput onTimeInput={mockOnTimeInput} />);

      const input = screen.getByLabelText(/enter your time/i);

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      await waitFor(() => {
        expect(mockOnTimeInput).toHaveBeenCalledWith(83);
      });
    });

    test('does not submit when Enter is pressed during submission', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<TimeInput onTimeInput={jest.fn()} />);

      const input = screen.getByLabelText(/enter your time/i);

      fireEvent.change(input, { target: { value: '1:23' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      const callCount = fetch.mock.calls.length;

      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      // Should not make additional fetch calls
      expect(fetch.mock.calls.length).toBe(callCount);
    });
  });
});
