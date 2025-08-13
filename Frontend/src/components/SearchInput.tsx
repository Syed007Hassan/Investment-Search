import React, { useRef, useEffect } from "react";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";

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
  placeholder = "Search companies...",
  isLoading = false,
  onClear,
}: SearchInputProps) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (
        e.key === "/" &&
        (e.target as HTMLElement)?.tagName !== "INPUT" &&
        (e.target as HTMLElement)?.tagName !== "TEXTAREA"
      ) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <form
      onSubmit={(e: React.FormEvent) => {
        e.preventDefault();
        onSearch();
      }}
      className="relative"
    >
      <div className="relative">
        <input
          ref={inputRef}
          id="company-search"
          aria-label="Search companies"
          type="text"
          value={value}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange(e.target.value)
          }
          className="w-full pr-24 pl-6 py-4 bg-white text-gray-900 rounded-lg border border-gray-300 shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/40 focus:border-brand dark:bg-gray-800 dark:text-gray-100 dark:border-gray-700 dark:placeholder-gray-500"
          placeholder={placeholder}
        />

        {value && (
          <button
            type="button"
            onClick={onClear}
            className="absolute right-12 top-1/2 -translate-y-1/2 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
            aria-label="Clear search"
          >
            Clear
          </button>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200"
          aria-label="Search"
        >
          {isLoading ? (
            <div className="animate-spin h-5 w-5 border-2 border-brand/70 rounded-full border-t-transparent"></div>
          ) : (
            <MagnifyingGlassIcon className="h-6 w-6" />
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchInput;
