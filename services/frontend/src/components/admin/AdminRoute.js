import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';  // Ensure jwt-decode is installed and imported

const AdminRoute = () => {
    const location = useLocation();
    const token = localStorage.getItem('token');
    let isAdmin = false;

    // Decode the JWT to verify if the user is an admin
    if (token) {
        try {
            const decoded = jwtDecode(token);
            isAdmin = decoded.is_admin;
        } catch (error) {
            console.error("Failed to decode JWT:", error);
        }
    }

    return token && isAdmin ? <Outlet /> : <Navigate to="/" replace state={{ from: location }} />;
};

export default AdminRoute;