import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import SearchInput from '../components/SearchInput';

interface Company {
  name: string;
  description: string;
  industry: string;
  size: string;
  location: string;
}

const CompanySearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/search-company', {
        query: searchQuery,
      });
      setCompanies(response.data.company_recommendations || []);
    } catch (error) {
      toast.error('Failed to search companies');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-xl p-6">
      <SearchInput
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search for companies..."
      />
      
      <div className="mt-8 space-y-4">
        {companies.map((company, index) => (
          <div 
            key={index} 
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 bg-white"
          >
            <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
            <p className="mt-2 text-gray-600">{company.description}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {company.industry}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {company.size}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                {company.location}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CompanySearch; 