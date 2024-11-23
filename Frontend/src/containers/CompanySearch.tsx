import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import SearchInput from '../components/SearchInput';
import ReactMarkdown from 'react-markdown';
import { Company } from '../types/company';

interface SearchResponse {
  response: string;
  company_recommendations: Company[];
  source: string;
}

const CompanySearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post<SearchResponse>('http://localhost:8000/search-company', {
        query: searchQuery,
      });
      setSearchResponse(response.data);
    } catch (error) {
      toast.error('Failed to search companies');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800/90 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-green-400/20">
      <SearchInput
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search for companies..."
      />
      
      {searchResponse && (
        <div className="mt-8 space-y-6">
          <div className="border border-green-400/20 rounded-lg p-4 bg-gray-800/50">
            <h2 className="text-lg font-semibold text-green-400 mb-2">Search Summary</h2>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown>
                {searchResponse.response}
              </ReactMarkdown>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-green-400">Recommended Companies</h2>
            {searchResponse.company_recommendations.map((company, index) => (
              <div 
                key={index} 
                className="border border-green-400/20 rounded-lg p-4 hover:shadow-lg hover:shadow-green-400/10 transition-all duration-300 bg-gray-800"
              >
                <h3 className="text-lg font-semibold text-green-400">{company.name}</h3>
                <p className="mt-2 text-gray-300">{company.description}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-green-400 border border-green-400/20">
                    {company.industry}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-green-400 border border-green-400/20">
                    {company.size}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-green-400 border border-green-400/20">
                    {company.location}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CompanySearch; 