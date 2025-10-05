import axios from 'axios';
import { getToken } from '@clerk/clerk-react';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:3000', // or your backend URL
});

// Add request interceptor to include auth token
api.interceptors.request.use(async (config) => {
  try {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    console.error('Error getting token:', error);
  }
  return config;
});

export default api;