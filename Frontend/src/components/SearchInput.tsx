import React, { useRef, useEffect } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  isLoading?: boolean;
  onClear?: () => void;
}

const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  onSearch,
  placeholder = 'Search companies...',
  isLoading = false,
  onClear,
}: SearchInputProps) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === '/' && (e.target as HTMLElement)?.tagName !== 'INPUT' && (e.target as HTMLElement)?.tagName !== 'TEXTAREA') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <form onSubmit={(e: React.FormEvent) => { e.preventDefault(); onSearch(); }} className="relative group">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-brand to-brand-dark rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
      <div className="relative">
        <input
          ref={inputRef}
          id="company-search"
          aria-label="Search companies"
          type="text"
          value={value}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
          className="w-full pr-24 pl-6 py-4 bg-gray-800 text-brand rounded-lg border border-brand/50 focus:border-brand focus:ring-2 focus:ring-brand focus:ring-opacity-50 focus:outline-none placeholder-brand/50 shadow-lg"
          placeholder={placeholder}
        />

        {value && (
          <button
            type="button"
            onClick={onClear}
            className="absolute right-12 top-1/2 -translate-y-1/2 text-sm text-brand hover:text-brand-dark"
            aria-label="Clear search"
          >
            Clear
          </button>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-brand hover:text-brand-dark transition-colors duration-200"
          aria-label="Search"
        >
          {isLoading ? (
            <div className="animate-spin h-6 w-6 border-2 border-brand rounded-full border-t-transparent"></div>
          ) : (
            <MagnifyingGlassIcon className="h-6 w-6" />
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchInput; 