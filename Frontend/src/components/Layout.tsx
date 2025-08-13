import React from "react";

interface LayoutProps {
  onAddCompany?: () => void;
  onViewAll?: () => void;
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({
  onAddCompany,
  onViewAll,
  children,
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <header className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-gray-900/60 bg-gray-900/80 border-b border-brand/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 select-none">
            <div className="h-8 w-8 bg-gradient-to-tr from-brand to-brand-dark rounded-lg" />
            <span className="font-semibold tracking-tight">
              Investment Search
            </span>
          </div>
          <div className="flex items-center gap-3">
            {onViewAll && (
              <button
                onClick={onViewAll}
                className="h-9 px-4 rounded-lg border border-brand/30 text-gray-200 hover:bg-gray-800/60 transition-colors"
              >
                View All
              </button>
            )}
            {onAddCompany && (
              <button
                onClick={onAddCompany}
                className="h-9 px-4 rounded-lg bg-gradient-to-r from-brand to-brand-dark text-gray-900 font-medium shadow hover:opacity-90 transition-opacity"
              >
                Add Company
              </button>
            )}
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {children}
      </main>
      <footer className="mt-10 border-t border-brand/20 py-6 text-center text-sm text-gray-400">
        <span>© {new Date().getFullYear()} Investment Search</span>
      </footer>
    </div>
  );
};

export default Layout;
