import axios from 'axios';

// Vite substitutes VITE_API_URL at build time. The fallback keeps local development working.
const configuredApiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
const normalizedApiUrl = configuredApiUrl.replace(/\/+$/, '');
const baseURL = normalizedApiUrl.endsWith('/api') ? normalizedApiUrl : `${normalizedApiUrl}/api`;

const API = axios.create({ baseURL });

API.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

API.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default API;
