import React from 'react';
import { Toaster } from 'react-hot-toast';
import CompanySearch from './containers/CompanySearch';
import AddCompany from './containers/AddCompany';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Toaster position="top-right" />
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Company Search & Ranking System</h1>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-8">
            <CompanySearch />
          </div>
          <div>
            <AddCompany />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
