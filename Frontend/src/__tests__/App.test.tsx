import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import App from '../App';

jest.mock('axios');
const mockedAxios = axios as unknown as jest.Mocked<{ get: jest.Mock; delete: jest.Mock }>;

describe('App', () => {
  it('renders routes and modals; loads companies, deletes one', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { companies: [
      { id: 1, name: 'Acme', description: 'D', industry: 'Tech', size: 'L', location: 'USA' }
    ] } });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // opens add modal
    await waitFor(() => expect(mockedAxios.get).toHaveBeenCalled());
    const addBtn = screen.getByRole('button', { name: /add company/i });
    await act(async () => {
      await userEvent.click(addBtn);
    });
    expect(screen.getByText(/add new company/i)).toBeInTheDocument();

    // open list and delete
    const listBtn = screen.getByRole('button', { name: /view all companies/i });
    await act(async () => {
      await userEvent.click(listBtn);
    });
    expect(await screen.findByText('Acme')).toBeInTheDocument();

    mockedAxios.delete.mockResolvedValueOnce({ status: 200 });
    mockedAxios.get.mockResolvedValueOnce({ data: { companies: [] } });
    const deleteButton = screen.getByTitle('Delete company');
    await act(async () => {
      await userEvent.click(deleteButton);
    });
    await waitFor(() => expect(mockedAxios.delete).toHaveBeenCalled());
  });
});

