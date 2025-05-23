import apiClient from './api';

const login = async (email, password) => {
    // FastAPI's OAuth2PasswordRequestForm expects 'username' and 'password'
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post('/users/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (response.data.access_token) {
        localStorage.setItem('accessToken', response.data.access_token);
        if (response.data.refresh_token) {
            localStorage.setItem('refreshToken', response.data.refresh_token);
        }
    }
    return response.data; // Contains tokens
};

const register = async (userData) => {
    // userData expected: { email, password, full_name (optional), ... }
    const response = await apiClient.post('/users/register', userData);
    return response.data; // Contains registered user info (excluding password)
};

const getCurrentUser = async () => {
    const response = await apiClient.get('/users/me');
    if (response.data) {
        localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
};

const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    // Optionally: notify backend about logout
};

export default {
    login,
    register,
    getCurrentUser,
    logout,
};
