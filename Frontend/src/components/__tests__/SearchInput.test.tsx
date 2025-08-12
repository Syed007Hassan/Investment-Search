import React from 'react';
import { render, screen, act, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchInput from '../SearchInput';

describe('SearchInput', () => {
  it('calls onChange and onSearch, shows/uses clear button, and focuses on "/"', async () => {
    const onChange = jest.fn();
    const onSearch = jest.fn();
    const onClear = jest.fn();
    render(
      <SearchInput
        value="abc"
        onChange={onChange}
        onSearch={onSearch}
        onClear={onClear}
        isLoading={false}
      />
    );

    const input = screen.getByLabelText('Search companies') as HTMLInputElement;
    
    await act(async () => {
      await userEvent.clear(input);
      await userEvent.type(input, 'xyz');
    });
    expect(onChange).toHaveBeenCalled();

    const clearBtn = screen.getByRole('button', { name: /clear/i });
    await act(async () => {
      await userEvent.click(clearBtn);
    });
    expect(onClear).toHaveBeenCalled();

    const form = input.closest('form')!;
    await act(async () => {
      fireEvent.submit(form);
    });
    expect(onSearch).toHaveBeenCalled();

    // Press "/" outside inputs to focus input
    await act(async () => {
      await userEvent.keyboard('/');
    });
    expect(document.activeElement).toBe(input);
  });

  it('shows spinner when loading', () => {
    render(
      <SearchInput value="" onChange={jest.fn()} onSearch={jest.fn()} isLoading />
    );
    expect(screen.getByLabelText('Search').firstChild).toHaveClass('animate-spin');
  });
});

