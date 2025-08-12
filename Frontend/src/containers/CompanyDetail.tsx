import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Company } from '../types/company';

const CompanyDetail: React.FC = () => {
  const params = useParams();
  const id = params.id as string | undefined;
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/companies/${id}`);
        const found: Company | null = res.data ?? null;
        if (!found || !found.id) {
          toast.error('Company not found');
          navigate('/');
          return;
        }
        setCompany(found);
      } catch (e) {
        toast.error('Failed to load company');
      } finally {
        setIsLoading(false);
      }
    };
    fetchCompany();
  }, [id, navigate]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto p-6">
        <div className="h-8 w-1/3 bg-gray-700 rounded animate-pulse" />
        <div className="mt-6 h-4 w-2/3 bg-gray-700 rounded animate-pulse" />
        <div className="mt-2 h-4 w-1/2 bg-gray-700 rounded animate-pulse" />
      </div>
    );
  }

  if (!company) return null;

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-4">
        <Link to="/" className="text-sm text-brand hover:underline">← Back to search</Link>
      </div>
      <div className="rounded-xl border border-brand/20 bg-gray-800 p-6">
        <h1 className="text-3xl font-bold text-brand">{company.name}</h1>
        <p className="mt-3 text-gray-300">{company.description}</p>
        <div className="mt-4 flex flex-wrap gap-2">
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
      </div>
    </div>
  );
};

export default CompanyDetail;

