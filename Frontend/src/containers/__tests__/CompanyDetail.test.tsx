import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import axios from 'axios';
import CompanyDetail from '../CompanyDetail';

jest.mock('axios');
const mockedAxios = axios as unknown as jest.Mocked<{ get: jest.Mock }>;

function renderWithRouter(initialEntries: string[]) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="/companies/:id" element={<CompanyDetail />} />
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('CompanyDetail', () => {
  it('loads and displays company', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: { id: 1, name: 'Acme', description: 'Desc', industry: 'Tech', size: 'Large', location: 'USA' },
    });

    renderWithRouter(['/companies/1']);

    await waitFor(() => expect(screen.getByText(/Back to search/i)).toBeInTheDocument());
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Acme' })).toBeInTheDocument());
  });

  it('redirects to home on not found', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: null });

    renderWithRouter(['/companies/999']);

    // After error, component navigates home
    await waitFor(() => expect(screen.getByText('Home')).toBeInTheDocument());
  });
});

