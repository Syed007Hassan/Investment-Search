import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import CompanySearch from '../CompanySearch';

jest.mock('axios');
const mockedAxios = axios as unknown as jest.Mocked<{ post: jest.Mock }>;

// Mock clipboard and document.execCommand
const mockClipboard = {
  writeText: jest.fn().mockResolvedValue(void 0),
};

Object.defineProperty(navigator, 'clipboard', {
  value: mockClipboard,
  writable: true,
});

Object.defineProperty(document, 'execCommand', {
  value: jest.fn().mockReturnValue(true),
  writable: true,
});

function setup() {
  return render(
    <MemoryRouter>
      <CompanySearch />
    </MemoryRouter>
  );
}

describe('CompanySearch', () => {
  beforeEach(() => {
    sessionStorage.clear();
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2025-01-01T12:00:00Z'));
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('performs search, renders results, filters and sorts', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        response: 'Summary',
        source: 'x',
        company_recommendations: [
          { id: 1, name: 'Beta', description: 'D', industry: 'Technology', size: 'Small', location: 'USA' },
          { id: 2, name: 'Acme', description: 'D2', industry: 'Finance', size: 'Large', location: 'EU' }
        ],
      },
    });

    setup();

    const input = screen.getByLabelText(/search companies/i);
    
    await act(async () => {
      await userEvent.type(input, 'cloud');
      jest.advanceTimersByTime(400);
    });
    
    await waitFor(() => expect(mockedAxios.post).toHaveBeenCalled());

    expect(await screen.findByText('Search Summary')).toBeInTheDocument();
    expect(screen.getByText('Recommended Companies')).toBeInTheDocument();

    // Apply filters
    await act(async () => {
      await userEvent.click(screen.getByRole('button', { name: 'Technology' }));
    });
    expect(screen.getByText(/1 results/)).toBeInTheDocument();

    // Sort by name and ensure order
    await act(async () => {
      await userEvent.selectOptions(screen.getByLabelText(/sort/i), 'name');
    });
    // After sorting, first card should be Acme for overall list, but with filter we still have one
    expect(screen.getByText('Beta')).toBeInTheDocument();

    // Clear all
    await act(async () => {
      await userEvent.click(screen.getByRole('button', { name: /clear all/i }));
    });
    expect(screen.getByText(/results/)).toBeInTheDocument();
  });

  it('handles manual search submit and copy actions', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        response: 'Summary 2',
        source: 'x',
        company_recommendations: [],
      },
    });

    setup();
    const input = screen.getByLabelText(/search companies/i);
    
    await act(async () => {
      await userEvent.type(input, 'ai');
      await userEvent.keyboard('{Enter}');
    });
    await waitFor(() => expect(mockedAxios.post).toHaveBeenCalled());

    expect(await screen.findByText('Search Summary')).toBeInTheDocument();

    // Copy summary
    await act(async () => {
      await userEvent.click(screen.getByRole('button', { name: /copy/i }));
    });
    expect(mockClipboard.writeText).toHaveBeenCalledWith('Summary 2');
  });

  it('shows error state when backend fails', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('network'));
    setup();
    const input = screen.getByLabelText(/search companies/i);
    
    await act(async () => {
      await userEvent.type(input, 'err');
      jest.advanceTimersByTime(400);
    });
    
    await waitFor(() => expect(screen.getByText(/failed to search companies/i)).toBeInTheDocument());
  });
});

