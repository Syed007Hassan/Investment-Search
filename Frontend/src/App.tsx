import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import CompanySearch from './containers/CompanySearch';
import AddCompany from './containers/AddCompany';
import Modal from './components/Modal';
import axios from 'axios';

function App() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isListModalOpen, setIsListModalOpen] = useState(false);
  const [companies, setCompanies] = useState([]);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get('http://localhost:8000/companies');
      setCompanies(response.data.companies);
    } catch (error) {
      console.error('Failed to fetch companies:', error);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-800 to-gray-900 text-white">
      <Toaster position="top-right" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-end space-x-4 mb-8">
          <button
            onClick={() => setIsListModalOpen(true)}
            className="px-4 py-2 bg-gray-800 text-green-400 rounded-lg shadow-lg border border-green-400 hover:bg-green-400 hover:text-gray-800 transition-all duration-300"
          >
            View All Companies
          </button>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-green-400 text-gray-800 rounded-lg shadow-lg border border-green-400 hover:bg-gray-800 hover:text-green-400 transition-all duration-300"
          >
            Add Company
          </button>
        </div>

        <div className="flex flex-col items-center justify-center">
          <h1 className="text-4xl font-bold text-green-400 mb-12 text-center">
            Company Search & Ranking System
          </h1>
          <div className="w-full max-w-3xl">
            <CompanySearch />
          </div>
        </div>
      </div>

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add New Company"
      >
        <AddCompany
          onSuccess={() => {
            setIsAddModalOpen(false);
            fetchCompanies();
          }}
        />
      </Modal>

      <Modal
        isOpen={isListModalOpen}
        onClose={() => setIsListModalOpen(false)}
        title="All Companies"
      >
        <div className="space-y-4 max-h-[60vh] overflow-y-auto">
          {companies.map((company: any, index) => (
            <div key={index} className="border border-green-400/20 rounded-lg p-4 hover:shadow-lg hover:shadow-green-400/10 transition-all duration-300 bg-gray-800">
              <h3 className="text-lg font-semibold text-green-400">{company.name}</h3>
              <p className="text-gray-300 text-sm mt-1">{company.description}</p>
              <div className="mt-2 flex flex-wrap gap-2">
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
      </Modal>
    </div>
  );
}

export default App;
