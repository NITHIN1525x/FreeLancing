// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import API from '../api/axios.js';

const AuthContext = createContext();

const storedValue = (key) => localStorage.getItem(key);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => {
        const storedUser = storedValue('user');
        return storedUser ? JSON.parse(storedUser) : null;
    });
    const [token, setToken] = useState(() => storedValue('access_token'));
    const [loading] = useState(false);

    const persistUser = useCallback((userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    }, []);

    const refreshUser = useCallback(async () => {
        const response = await API.get('/profile/');
        persistUser(response.data);
        return response.data;
    }, [persistUser]);

    useEffect(() => {
        if (token) {
            refreshUser().catch(() => {
                // Keep the cached profile if the server is temporarily unreachable.
            });
        }
    }, [token, refreshUser]);

    const login = (userData, accessToken) => {
        persistUser(userData);
        setToken(accessToken);
        localStorage.setItem('access_token', accessToken);
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.clear();
        window.location.href = '/';
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, refreshUser, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
