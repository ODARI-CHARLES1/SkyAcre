// This file sets up a configured axios instance for making HTTP requests to the backend API.
// It includes automatic authentication token inclusion using Clerk.

// Import axios library for making HTTP requests
import axios from 'axios';
// Import getToken function from Clerk to retrieve the authentication token
import { getToken } from '@clerk/clerk-react';

// Create an axios instance with default configuration
// This instance will be used throughout the app for API calls
const api = axios.create({
  baseURL: 'http://localhost:3000', // Base URL for the backend server (change for production)
});

// Add a request interceptor to automatically include the auth token in requests
// Interceptors run before each request is sent
api.interceptors.request.use(async (config) => {
  // Try to get the authentication token from Clerk
  try {
    const token = await getToken(); // Asynchronously get the token
    if (token) {
      // If token exists, add it to the request headers as Bearer token
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    // If there's an error getting the token, log it (but don't fail the request)
    console.error('Error getting token:', error);
  }
  // Return the modified config to proceed with the request
  return config;
});

// Export the configured api instance as the default export
export default api;