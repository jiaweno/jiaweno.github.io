import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api/v1', // Matches Vite proxy and FastAPI prefix
    // timeout: 10000, // Optional: timeout
    // headers: { 'Content-Type': 'application/json' } // Default, can be overridden
});

// Request interceptor to add JWT token to headers
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Optional: Response interceptor for handling global errors like 401
apiClient.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            // Handle unauthorized access, e.g., redirect to login, clear token
            // localStorage.removeItem('accessToken');
            // localStorage.removeItem('refreshToken');
            // localStorage.removeItem('user');
            // window.location.href = '/login'; // Or use react-router navigate
            console.error("Unauthorized access - 401. Implement token refresh or redirect.");
        }
        return Promise.reject(error);
    }
);

export default apiClient;
