import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';
import apiClient from '../services/api'; // For direct use if needed

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext); // Corrected: call useContext

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true); // Initial check for token/user
    const [error, setError] = useState(null);

    useEffect(() => {
        const initializeAuth = async () => {
            const token = localStorage.getItem('accessToken');
            const storedUser = localStorage.getItem('user');
            if (token) {
                if (storedUser) {
                    setUser(JSON.parse(storedUser));
                }
                // Optionally: verify token with backend or fetch user data if not stored
                try {
                    // If user not stored, or to refresh/validate
                    const currentUser = await authService.getCurrentUser();
                    setUser(currentUser);
                } catch (e) {
                    console.error("Failed to fetch current user on init:", e);
                    authService.logout(); // Clear invalid token/user
                    setUser(null);
                }
            }
            setLoading(false);
        };
        initializeAuth();
    }, []);

    const login = async (email, password) => {
        try {
            setLoading(true);
            setError(null);
            const tokenData = await authService.login(email, password);
            // After login, fetch user details to store in context
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            setLoading(false);
            return currentUser;
        } catch (err) {
            console.error("Login failed:", err.response?.data?.detail || err.message);
            setError(err.response?.data?.detail || 'Login failed');
            setLoading(false);
            throw err;
        }
    };

    const register = async (userData) => {
        try {
            setLoading(true);
            setError(null);
            const registeredUser = await authService.register(userData);
            // Optionally log in the user directly after registration
            // await login(userData.email, userData.password);
            setLoading(false);
            return registeredUser;
        } catch (err) {
            console.error("Registration failed:", err.response?.data?.detail || err.message);
            setError(err.response?.data?.detail || 'Registration failed');
            setLoading(false);
            throw err;
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
        // navigate to home or login page could be handled by components listening to auth state
    };

    const fetchCurrentUser = async () => { // Expose a way to refetch user
        try {
           const currentUser = await authService.getCurrentUser();
           setUser(currentUser);
           return currentUser;
        } catch (e) {
           authService.logout();
           setUser(null);
           throw e;
        }
      };

    const value = {
        user,
        isAuthenticated: !!user,
        loading,
        error,
        login,
        register,
        logout,
        fetchCurrentUser 
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
