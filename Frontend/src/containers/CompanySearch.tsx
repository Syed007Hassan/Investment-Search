import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import SearchInput from '../components/SearchInput';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { Company } from '../types/company';
import { useDebounce } from '../hooks/useDebounce';
import { Link } from 'react-router-dom';

interface SearchResponse {
  response: string;
  company_recommendations: Company[];
  source: string;
}

const CompanySearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<{ industry: string[]; size: string[]; location: string[] }>({ industry: [], size: [], location: [] });
  const [sortBy, setSortBy] = useState<'relevance' | 'name'>('relevance');
  const debouncedQuery = useDebounce(searchQuery, 400);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // hydrate from URL or sessionStorage on mount
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const urlQuery = params.get('q') || '';
      const urlSort = (params.get('sort') as 'relevance' | 'name') || 'relevance';
      const parseList = (key: string) => (params.get(key) ? (params.get(key) as string).split(',').filter(Boolean) : []);
      const urlFilters = {
        industry: parseList('industry'),
        size: parseList('size'),
        location: parseList('location'),
      };

      const storedRaw = sessionStorage.getItem('companySearchState');
      const stored = storedRaw ? JSON.parse(storedRaw) as { q: string; sort: 'relevance' | 'name'; filters: { industry: string[]; size: string[]; location: string[] } } : null;

      // URL takes precedence; otherwise fall back to session state
      const effectiveQuery = urlQuery || stored?.q || '';
      const effectiveSort = params.get('sort') ? urlSort : (stored?.sort || 'relevance');
      const effectiveFilters = (params.get('industry') || params.get('size') || params.get('location')) ? urlFilters : (stored?.filters || { industry: [], size: [], location: [] });

      setSearchQuery(effectiveQuery);
      setSortBy(effectiveSort);
      setFilters(effectiveFilters);
      // If we have a query (from either source), search will trigger via debounced effect
    } catch {
      // ignore
    }
  }, []);

  const handleSearch = async (q?: string) => {
    const query = (q ?? searchQuery).trim();
    if (!query) return;

    setIsLoading(true);
    try {
      const response = await axios.post<SearchResponse>('http://localhost:8000/search-company', {
        query,
        filters,
        sort_by: sortBy,
      });
      setSearchResponse(response.data);
      setError(null);
      setLastUpdated(new Date());
    } catch (error) {
      setError('Failed to search companies');
      toast.error('Failed to search companies');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (debouncedQuery.trim()) {
      handleSearch(debouncedQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, JSON.stringify(filters), sortBy]);

  // persist state to URL and sessionStorage
  useEffect(() => {
    const url = new URL(window.location.href);
    const setList = (key: string, list: string[]) => {
      if (list.length) url.searchParams.set(key, list.join(','));
      else url.searchParams.delete(key);
    };
    if (searchQuery) url.searchParams.set('q', searchQuery);
    else url.searchParams.delete('q');
    url.searchParams.set('sort', sortBy);
    setList('industry', filters.industry);
    setList('size', filters.size);
    setList('location', filters.location);
    window.history.replaceState(null, '', url.toString());

    const payload = { q: searchQuery, sort: sortBy, filters };
    sessionStorage.setItem('companySearchState', JSON.stringify(payload));
  }, [searchQuery, filters, sortBy]);

  const filteredAndSorted = useMemo(() => {
    if (!searchResponse) return [] as Company[];
    let companies = [...searchResponse.company_recommendations];
    // local fallback filtering if backend ignores filters
    if (filters.industry.length) companies = companies.filter(c => filters.industry.includes(c.industry));
    if (filters.size.length) companies = companies.filter(c => filters.size.includes(c.size));
    if (filters.location.length) companies = companies.filter(c => filters.location.includes(c.location));
    if (sortBy === 'name') companies.sort((a, b) => a.name.localeCompare(b.name));
    return companies;
  }, [searchResponse, filters, sortBy]);

  const toggleChip = (group: 'industry' | 'size' | 'location', value: string) => {
    setFilters((prev: { industry: string[]; size: string[]; location: string[] }) => {
      const has = prev[group].includes(value);
      const nextValues = has ? prev[group].filter((v: string) => v !== value) : [...prev[group], value];
      return { ...prev, [group]: nextValues };
    });
  };

  const clearAllFilters = () => setFilters({ industry: [], size: [], location: [] });

  return (
    <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-brand/20">
      <SearchInput
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={() => handleSearch()}
        isLoading={isLoading}
        placeholder="Search for companies..."
        onClear={() => setSearchQuery('')}
      />
      {/* Controls: result count, sort, filters */}
      <div className="mt-6 flex flex-col gap-4">
        <div className="flex flex-wrap items-center gap-3 justify-between">
          <div className="text-sm text-gray-300">
            {isLoading ? 'Searching…' : `${filteredAndSorted.length || 0} results`}
            {lastUpdated && !isLoading && (
              <span className="ml-2 text-gray-500">· updated {lastUpdated.toLocaleTimeString()}</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="sort" className="text-sm text-gray-300">Sort</label>
            <select
              id="sort"
              value={sortBy}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSortBy(e.target.value as 'relevance' | 'name')}
              className="rounded-md bg-gray-800 border border-brand/30 text-gray-200"
            >
              <option value="relevance">Relevance</option>
              <option value="name">Name</option>
            </select>
            {(filters.industry.length + filters.size.length + filters.location.length) > 0 && (
              <button onClick={clearAllFilters} className="text-sm text-brand hover:text-brand-dark">Clear all</button>
            )}
          </div>
        </div>

        {/* Filter chips (static examples; you can wire with dynamic facets later) */}
        <div className="flex flex-wrap gap-2">
          {['Technology', 'Finance', 'Healthcare'].map((v: string) => (
            <button
              type="button"
              key={`industry-${v}`}
              onClick={() => toggleChip('industry', v)}
              className={`px-3 py-1 rounded-full text-xs border ${filters.industry.includes(v) ? 'bg-brand/10 text-brand border-brand/40' : 'bg-gray-800 text-gray-300 border-gray-700'}`}
            >
              {v}
            </button>
          ))}
          {['Small', 'Medium', 'Large'].map((v: string) => (
            <button
              type="button"
              key={`size-${v}`}
              onClick={() => toggleChip('size', v)}
              className={`px-3 py-1 rounded-full text-xs border ${filters.size.includes(v) ? 'bg-brand/10 text-brand border-brand/40' : 'bg-gray-800 text-gray-300 border-gray-700'}`}
            >
              {v}
            </button>
          ))}
          {['USA', 'EU', 'APAC'].map((v: string) => (
            <button
              type="button"
              key={`location-${v}`}
              onClick={() => toggleChip('location', v)}
              className={`px-3 py-1 rounded-full text-xs border ${filters.location.includes(v) ? 'bg-brand/10 text-brand border-brand/40' : 'bg-gray-800 text-gray-300 border-gray-700'}`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {/* States: empty, error, loading */}
      <div className="mt-8">
        {!searchResponse && !isLoading && (
          <div className="text-center text-gray-400">
            Start by searching for a company or try filters above.
          </div>
        )}

        {error && (
          <div className="rounded-md border border-red-500/30 bg-red-500/10 p-3 text-red-300">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-brand/10 bg-gray-800 p-4 animate-pulse space-y-3">
                <div className="h-5 w-2/3 bg-gray-700 rounded" />
                <div className="h-4 w-full bg-gray-700 rounded" />
                <div className="h-4 w-5/6 bg-gray-700 rounded" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      {searchResponse && !isLoading && (
        <div className="mt-8 space-y-6">
          <div className="border border-brand/20 rounded-lg p-4 bg-gray-800/50">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-brand">Search Summary</h2>
              <div className="flex gap-2 text-sm">
                <button
                  className="text-brand hover:text-brand-dark"
                  onClick={() => navigator.clipboard.writeText(searchResponse.response)}
                >
                  Copy
                </button>
                <button
                  className="text-brand hover:text-brand-dark"
                  onClick={() => {
                    const url = new URL(window.location.href);
                    url.searchParams.set('q', searchQuery);
                    window.navigator.clipboard.writeText(url.toString());
                    toast.success('Share link copied');
                  }}
                >
                  Share
                </button>
              </div>
            </div>
            <div className="prose prose-invert max-w-none mt-2">
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
                {searchResponse.response}
              </ReactMarkdown>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-brand">Recommended Companies</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAndSorted.map((company: Company, index: number) => (
                <Link
                  to={`/companies/${company.id}`}
                  key={index}
                  className="border border-brand/20 rounded-lg p-4 hover:shadow-lg hover:shadow-brand/10 transition-all duration-300 bg-gray-800 block"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-base font-semibold text-brand">{company.name}</h3>
                  </div>
                  <p className="mt-2 text-gray-300 line-clamp-3">{company.description}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-brand border border-brand/20">
                      {company.industry}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-brand border border-brand/20">
                      {company.size}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-brand border border-brand/20">
                      {company.location}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
            {filteredAndSorted.length === 0 && (
              <div className="text-center text-gray-400">No results — try clearing some filters.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CompanySearch; 