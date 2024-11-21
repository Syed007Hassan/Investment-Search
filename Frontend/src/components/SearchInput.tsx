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
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder={placeholder}
        onKeyPress={(e) => e.key === 'Enter' && onSearch()}
      />
      <button
        onClick={onSearch}
        disabled={isLoading}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-gray-700"
      >
        {isLoading ? (
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent" />
        ) : (
          <MagnifyingGlassIcon className="h-5 w-5" />
        )}
      </button>
    </div>
  );
};

export default SearchInput; 