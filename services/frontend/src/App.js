import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/authentication/AuthContext';

import Header from './components/Header';
import HomePage from './components/HomePage';
import LoginPage from './components/LoginPage';
import PrivateRoute from './components/PrivateRoute';
import SignupPage from './components/SignupPage';
import AdminRoute from './components/admin/AdminRoute';
import AdminDashboard from './components/admin/AdminDashboard';
import SearchSettingDetail from './components/searchSetting/SearchSettingDetail';

function App() {
  return (
    <AuthProvider>
    <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/" element={<PrivateRoute />}>
            <Route index element={<HomePage />} />
          </Route>
          <Route path="/settings/detail/:id" element={<PrivateRoute />}>
            <Route index element={<SearchSettingDetail />} />
          </Route>
          <Route path="/admin" element={<AdminRoute />}>
            <Route index element={<AdminDashboard />} />
          </Route>
          <Route path="*" element={<Navigate replace to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
