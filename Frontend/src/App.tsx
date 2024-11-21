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
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
      <Toaster position="top-right" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-end space-x-4 mb-8">
          <button
            onClick={() => setIsListModalOpen(true)}
            className="px-4 py-2 bg-white text-purple-600 rounded-lg shadow hover:bg-gray-50 transition-colors"
          >
            View All Companies
          </button>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg shadow hover:bg-purple-700 transition-colors"
          >
            Add Company
          </button>
        </div>

        <div className="flex flex-col items-center justify-center">
          <h1 className="text-4xl font-bold text-white mb-8 text-center">
            Company Search System
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
            <div key={index} className="border rounded-lg p-4">
              <h3 className="font-semibold text-lg">{company.name}</h3>
              <p className="text-gray-600 text-sm mt-1">{company.description}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                  {company.industry}
                </span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  {company.size}
                </span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
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
