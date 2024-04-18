import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';

const PrivateRoute = () => {
    const location = useLocation();
    const isLoggedIn = localStorage.getItem('token');
  
    return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace state={{ from: location }} />;
  };
  

export default PrivateRoute;