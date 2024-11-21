import React from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  isLoading?: boolean;
}

const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  onSearch,
  placeholder = 'Search companies...',
  isLoading = false,
}) => {
  return (
    <div className="relative group">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-green-400 to-green-600 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-6 py-4 bg-gray-800 text-green-400 rounded-lg border border-green-400/50 focus:border-green-400 focus:ring-2 focus:ring-green-400 focus:ring-opacity-50 focus:outline-none placeholder-green-400/50 shadow-lg"
          placeholder={placeholder}
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
        />
        <button
          onClick={onSearch}
          disabled={isLoading}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-green-400 hover:text-green-300 transition-colors duration-200"
        >
          {isLoading ? (
            <div className="animate-spin h-6 w-6 border-2 border-green-400 rounded-full border-t-transparent"></div>
          ) : (
            <MagnifyingGlassIcon className="h-6 w-6" />
          )}
        </button>
      </div>
    </div>
  );
};

export default SearchInput; 