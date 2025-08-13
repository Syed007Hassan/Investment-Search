import React, { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import CompanySearch from "./containers/CompanySearch";
import AddCompany from "./containers/AddCompany";
import CompanyDetail from "./containers/CompanyDetail";
import { Routes, Route } from "react-router-dom";
import Modal from "./components/Modal";
import axios from "axios";
import { TrashIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { Company } from "./types/company";
import Layout from "./components/Layout";

function App() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isListModalOpen, setIsListModalOpen] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get("http://localhost:8000/companies");
      if (response.data && Array.isArray(response.data.companies)) {
        setCompanies(response.data.companies);
      } else {
        console.error("Invalid response format:", response.data);
        toast.error("Failed to fetch companies");
      }
    } catch (error) {
      console.error("Failed to fetch companies:", error);
      toast.error("Failed to fetch companies");
    }
  };

  const deleteCompany = async (companyId: number) => {
    if (typeof companyId !== "number") {
      console.error("Invalid company ID:", companyId);
      toast.error("Invalid company ID");
      return;
    }

    try {
      const response = await axios.delete(
        `http://localhost:8000/companies/${companyId}`
      );
      if (response.status === 200) {
        toast.success("Company deleted successfully");
        fetchCompanies(); // Refresh the list
      } else {
        throw new Error("Failed to delete company");
      }
    } catch (error) {
      console.error("Failed to delete company:", error);
      toast.error("Failed to delete company");
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <Layout
      onAddCompany={() => setIsAddModalOpen(true)}
      onViewAll={() => setIsListModalOpen(true)}
    >
      <Toaster position="top-right" />
      <div className="w-full max-w-4xl mx-auto">
        <Routes>
          <Route path="/" element={<CompanySearch />} />
          <Route path="/companies/:id" element={<CompanyDetail />} />
        </Routes>
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
          {companies.map((company: Company) => (
            <div
              key={company.id}
              className="border border-brand/20 rounded-lg p-4 hover:shadow-lg transition-all duration-300 bg-gray-800 relative"
            >
              <button
                onClick={() => {
                  if (company.id) {
                    deleteCompany(company.id);
                  } else {
                    toast.error("Company ID not found");
                  }
                }}
                className="absolute top-4 right-4 p-1.5 text-red-400 hover:text-red-300 transition-colors duration-200 rounded-full hover:bg-red-400/10"
                title="Delete company"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
              <h3 className="text-lg font-semibold text-brand pr-8">
                {company.name}
              </h3>
              <p className="text-gray-300 text-sm mt-1">
                {company.description}
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
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
          ))}
        </div>
      </Modal>
    </Layout>
  );
}

export default App;
