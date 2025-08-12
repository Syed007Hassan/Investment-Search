// Jest setup for CRA tests
import '@testing-library/jest-dom';

// Mock matchMedia for components that may use it
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }),
});

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn().mockResolvedValue(undefined),
    readText: jest.fn().mockResolvedValue(''),
  },
});

// Silence react-hot-toast side effects in tests
jest.mock('react-hot-toast', () => {
  const actual = jest.requireActual('react-hot-toast');
  return {
    __esModule: true,
    ...actual,
    default: {
      success: jest.fn(),
      error: jest.fn(),
    },
    success: jest.fn(),
    error: jest.fn(),
    Toaster: () => null,
  };
});

// Use modern fake timers when tests opt-in
// (individual tests can call jest.useFakeTimers())

// Mock ESM modules that Jest (CRA) may struggle with
jest.mock('react-markdown', () => ({
  __esModule: true,
  default: () => null,
}));
jest.mock('remark-gfm', () => ({ __esModule: true, default: () => null }));
jest.mock('rehype-sanitize', () => ({ __esModule: true, default: () => null }));

// Mock axios globally to avoid ESM transform issues and control network at tests
jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  },
}));
