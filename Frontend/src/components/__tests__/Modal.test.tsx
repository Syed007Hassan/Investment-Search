import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from '../Modal';

describe('Modal', () => {
  it('does not render when closed', () => {
    const { container } = render(
      <Modal isOpen={false} onClose={jest.fn()} title="Test">
        <div>Content</div>
      </Modal>
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders content and title when open and closes on backdrop click', async () => {
    const onClose = jest.fn();
    render(
      <Modal isOpen onClose={onClose} title="My Title">
        <div>Content</div>
      </Modal>
    );
    expect(screen.getByText('My Title')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();

    const backdrop = document.querySelector('.absolute.inset-0.bg-gray-900.opacity-75') as HTMLElement;
    await userEvent.click(backdrop);
    expect(onClose).toHaveBeenCalled();
  });
});

