import React, { useState } from 'react';
import API from './api/axios';
import { useNavigate } from 'react-router-dom';

const SignupPage = () => {
  const [userData, setUserData] = useState({
    username: '',
    password: ''
  });
  const navigate = useNavigate();

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setUserData({
      ...userData,
      [name]: value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // Ensure the endpoint matches your FastAPI route for registration
      await API.post('/signup/', userData);
      alert('Signup successful!');
      navigate('/login');  // Redirect to login page after successful signup
    } catch (error) {
      console.error('Signup failed:', error.response ? error.response.data : error);
      alert('Signup failed: ' + (error.response ? error.response.data.detail : "Network Error"));
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Username:
          <input
            type="text"
            name="username"
            value={userData.username}
            onChange={handleInputChange}
            required
          />
        </label>
        <label>
          Password:
          <input
            type="password"
            name="password"
            value={userData.password}
            onChange={handleInputChange}
            required
          />
        </label>
        <button type="submit">Signup</button>
      </form>
    </div>
  );
};

export default SignupPage;