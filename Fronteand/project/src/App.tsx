import React, { useState, useEffect } from 'react';
import { useStore } from './store/useStore';
import { Login } from './components/Login';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { FarmerManagement } from './components/FarmerManagement';
import { Chat } from './components/Chat';
import { TaskManagement } from './components/TaskManagement';

function App() {
  const { isAuthenticated, updateDashboardStats } = useStore();
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    updateDashboardStats();
  }, [updateDashboardStats]);

  if (!isAuthenticated) {
    return <Login />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'farmers':
        return <FarmerManagement />;
      case 'chat':
        return <Chat />;
      case 'tasks':
        return <TaskManagement />;
      case 'reports':
        return (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Reports</h2>
            <p className="text-gray-600">Advanced reporting features coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Settings</h2>
            <p className="text-gray-600">System settings will be available here...</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout currentPage={currentPage} onPageChange={setCurrentPage}>
      {renderPage()}
    </Layout>
  );
}

export default App;