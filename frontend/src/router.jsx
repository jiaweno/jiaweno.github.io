import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './components/common/ProtectedRoute'; 

// New imports for Learning Path pages
import LearningPathsPage from './pages/LearningPathsPage';
import CreateLearningPathPage from './pages/CreateLearningPathPage';
import EditLearningPathPage from './pages/EditLearningPathPage';
import ViewLearningPathPage from './pages/ViewLearningPathPage';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/learning-paths" 
        element={
          <ProtectedRoute>
            <LearningPathsPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/learning-paths/create" 
        element={
          <ProtectedRoute>
            <CreateLearningPathPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/learning-paths/edit/:pathId" 
        element={
          <ProtectedRoute>
            <EditLearningPathPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/learning-paths/:pathId" 
        element={
          <ProtectedRoute>
            <ViewLearningPathPage />
          </ProtectedRoute>
        } 
      />

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;
