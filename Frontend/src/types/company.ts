export interface Company {
  id: number; // may be negative for web-only results
  name: string;
  description: string;
  industry: string;
  size: string;
  location: string;
  external_url?: string; // present for web-only results
}
