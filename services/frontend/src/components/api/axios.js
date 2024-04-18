import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/',  // Adjust this to your backend server's address
});

API.interceptors.request.use(
  function(config) {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  function(error) {
    return Promise.reject(error);
  }
);

export default API;