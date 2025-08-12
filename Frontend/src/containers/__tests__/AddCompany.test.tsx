import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import AddCompany from '../AddCompany';

jest.mock('axios');
const mockedAxios = axios as unknown as jest.Mocked<{ post: jest.Mock }>;

describe('AddCompany', () => {
  it('submits form successfully and resets fields', async () => {
    mockedAxios.post.mockResolvedValueOnce({ status: 200 });
    const onSuccess = jest.fn();

    render(<AddCompany onSuccess={onSuccess} />);

    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Company Name/i), 'Acme');
      await userEvent.type(screen.getByLabelText(/Description/i), 'Desc');
      await userEvent.type(screen.getByLabelText(/Industry/i), 'Tech');
      await userEvent.type(screen.getByLabelText(/Size/i), 'Large');
      await userEvent.type(screen.getByLabelText(/Location/i), 'USA');
    });

    await act(async () => {
      await userEvent.click(screen.getByRole('button', { name: /add company/i }));
    });

    await waitFor(() => expect(mockedAxios.post).toHaveBeenCalled());
    expect(onSuccess).toHaveBeenCalled();

    // fields reset
    expect((screen.getByLabelText(/Company Name/i) as HTMLInputElement).value).toBe('');
  });

  it('handles error path', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('fail'));
    render(<AddCompany />);

    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Company Name/i), 'Acme');
      await userEvent.type(screen.getByLabelText(/Description/i), 'Desc');
      await userEvent.type(screen.getByLabelText(/Industry/i), 'Tech');
      await userEvent.type(screen.getByLabelText(/Size/i), 'Large');
      await userEvent.type(screen.getByLabelText(/Location/i), 'USA');
      await userEvent.click(screen.getByRole('button', { name: /add company/i }));
    });

    await waitFor(() => expect(mockedAxios.post).toHaveBeenCalled());
  });
});

