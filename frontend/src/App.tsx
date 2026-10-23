// Root application component with routing and TanStack Query provider

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { IntakePage } from './pages/IntakePage';
import { JobPage } from './pages/JobPage';
import { DraftPage } from './pages/DraftPage';

// Initialize query client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<IntakePage />} />
              <Route path="/jobs/:id" element={<JobPage />} />
              <Route path="/jobs/:id/draft/:draftId" element={<DraftPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer className="border-t border-zinc-900 py-6 text-center text-xs text-zinc-500">
            ScholarPilot • Built for TetraNoodle AI Hackathon 2026 • Evidence-Backed Scholarship Research
          </footer>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
