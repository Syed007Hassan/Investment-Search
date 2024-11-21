import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface CompanyForm {
  name: string;
  description: string;
  industry: string;
  size: string;
  location: string;
}

interface AddCompanyProps {
  onSuccess?: () => void;
}

const AddCompany: React.FC<AddCompanyProps> = ({ onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<CompanyForm>({
    name: '',
    description: '',
    industry: '',
    size: '',
    location: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await axios.post('http://localhost:8000/companies', formData);
      toast.success('Company added successfully');
      setFormData({
        name: '',
        description: '',
        industry: '',
        size: '',
        location: '',
      });
      onSuccess?.();
    } catch (error) {
      toast.error('Failed to add company');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-green-400">
            Company Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md bg-gray-700 border-green-400/20 text-green-400 shadow-sm focus:border-green-400 focus:ring focus:ring-green-400 focus:ring-opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={4}
            className="mt-1 block w-full rounded-md bg-gray-700 border-green-400/20 text-green-400 shadow-sm focus:border-green-400 focus:ring focus:ring-green-400 focus:ring-opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400">Industry</label>
          <input
            type="text"
            name="industry"
            value={formData.industry}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md bg-gray-700 border-green-400/20 text-green-400 shadow-sm focus:border-green-400 focus:ring focus:ring-green-400 focus:ring-opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400">Size</label>
          <input
            type="text"
            name="size"
            value={formData.size}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md bg-gray-700 border-green-400/20 text-green-400 shadow-sm focus:border-green-400 focus:ring focus:ring-green-400 focus:ring-opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400">Location</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md bg-gray-700 border-green-400/20 text-green-400 shadow-sm focus:border-green-400 focus:ring focus:ring-green-400 focus:ring-opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-green-400 rounded-md shadow-sm text-sm font-medium text-gray-800 bg-green-400 hover:bg-gray-800 hover:text-green-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Adding...
            </span>
          ) : (
            'Add Company'
          )}
        </button>
      </form>
    </div>
  );
};

export default AddCompany; 