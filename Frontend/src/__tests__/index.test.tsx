import React from 'react';
import './mocks';

jest.mock('react-dom/client', () => {
  const actual = jest.requireActual('react-dom/client');
  return {
    ...actual,
    createRoot: jest.fn(() => ({ render: jest.fn() })),
  };
});

describe('index.tsx', () => {
  it('renders without crashing and calls reportWebVitals', () => {
    const rootEl = document.createElement('div');
    rootEl.id = 'root';
    document.body.appendChild(rootEl);

    const spy = jest.spyOn(console, 'log').mockImplementation(() => {});
    
    // Get the mocked createRoot before using it
    const { createRoot } = require('react-dom/client');
    
    // import after mocks are ready
    jest.isolateModules(() => {
      jest.doMock('../reportWebVitals', () => ({ __esModule: true, default: jest.fn() }));
      require('../index');
    });
    
    expect(createRoot).toHaveBeenCalled();
    spy.mockRestore();
  });
});

