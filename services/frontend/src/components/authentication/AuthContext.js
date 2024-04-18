import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [authState, setAuthState] = useState({
        isAuthenticated: false,
        isAdmin: false
    });

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const decoded = jwtDecode(token);  // Decode your token to find out if the user is an admin
            setAuthState({
                isAuthenticated: !!token,
                isAdmin: decoded.is_admin  // Adjust based on how admin data is stored in your token
            });
        }
    }, []);

    const login = (token) => {
        localStorage.setItem('token', token);
        const decoded = jwtDecode(token);  // Decode token to check admin status
        console.log(decoded);
        setAuthState({
            isAuthenticated: true,
            isAdmin: decoded.is_admin  // Adjust the condition based on your token structure
        });
    };

    const logout = () => {
        localStorage.removeItem('token');
        setAuthState({
            isAuthenticated: false,
            isAdmin: false
        });
    };

    return (
        <AuthContext.Provider value={{ authState, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);