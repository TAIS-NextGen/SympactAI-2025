// src/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // send cookies for auth if any
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- AUTH ---

export const registerUser = (userData) => {
  // userData should include: username, email, password, confirmPassword, companyId, role, rememberMe
  return api.post('/auth/register', userData);
};

export const loginUser = (credentials) => {
  // credentials: { email, password, rememberMe }
  return api.post('/auth/login', credentials);
};

export const logoutUser = () => {
  return api.post('/auth/logout');
};

// --- COMPANY ---

export const getCompanyInfo = () => {
  return api.get('/company/info');
};

export const updateCompanyInfo = (updateData) => {
  // updateData: object with company details to update
  return api.put('/company/update', updateData);
};

export const getCompanyUsers = () => {
  return api.get('/company/users');
};

export const getCompanyDashboard = () => {
  return api.get('/company/dashboard');
};

// --- PUMPS ---

export const getAllPumps = () => {
  return api.get('/pumps');
};

export const addPump = (pumpData) => {
  // pumpData: object with pump details
  return api.post('/pumps/add', pumpData);
};

export const getPumpDashboard = (id) => {
  if (id) {
    return api.get(`/pumps/dashboard/${id}`);
  } else {
    return api.get('/pumps/dashboard');
  }
};

// --- USER ---

export const getUserProfile = () => {
  return api.get('/user/profile');
};

export default api;
