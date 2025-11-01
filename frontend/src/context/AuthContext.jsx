/**
 * Authentication Context
 * Manages user authentication state across the application
 */
import { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Load user on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error('Failed to load user:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  const login = async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await authAPI.login(formData);
    const { access_token } = response.data;

    localStorage.setItem('token', access_token);
    setToken(access_token);

    // Fetch user data
    const userResponse = await authAPI.getCurrentUser();
    setUser(userResponse.data);

    return userResponse.data;
  };

  const register = async (email, password, full_name) => {
    const response = await authAPI.register({ email, password, full_name });
    const { access_token } = response.data;

    localStorage.setItem('token', access_token);
    setToken(access_token);

    // Fetch user data
    const userResponse = await authAPI.getCurrentUser();
    setUser(userResponse.data);

    return userResponse.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
