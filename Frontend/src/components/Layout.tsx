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
  const [theme, setTheme] = React.useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "dark";
    return (localStorage.getItem("theme") as "light" | "dark") || "dark";
  });

  React.useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") root.classList.add("dark");
    else root.classList.remove("dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const isDark = theme === "dark";

  return (
    <div
      className={`min-h-screen bg-gradient-to-br from-white via-gray-50 to-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 text-gray-900 dark:text-white`}
    >
      <header className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-white/70 bg-white/80 border-b border-gray-200 dark:supports-[backdrop-filter]:bg-gray-900/60 dark:bg-gray-900/80 dark:border-brand/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 select-none">
            <div className="h-8 w-8 bg-gradient-to-tr from-brand to-brand-dark rounded-lg shadow" />
            <span className="font-semibold tracking-tight">
              Investment Search
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setTheme(isDark ? "light" : "dark")}
              className="h-9 px-3 rounded-lg border border-gray-300 text-gray-800 hover:bg-gray-100 transition-colors dark:border-brand/30 dark:text-gray-200 dark:hover:bg-gray-800/60"
            >
              {isDark ? "Light" : "Dark"}
            </button>
            {onViewAll && (
              <button
                onClick={onViewAll}
                className="h-9 px-4 rounded-lg border border-gray-300 text-gray-800 hover:bg-gray-100 transition-colors dark:border-brand/30 dark:text-gray-200 dark:hover:bg-gray-800/60"
              >
                View All
              </button>
            )}
            {onAddCompany && (
              <button
                onClick={onAddCompany}
                className="h-9 px-4 rounded-lg bg-gradient-to-r from-brand to-brand-dark text-white font-medium shadow hover:opacity-90 transition-opacity"
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
