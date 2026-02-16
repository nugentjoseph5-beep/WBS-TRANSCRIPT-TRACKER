import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from './api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
      // Verify token is still valid
      authAPI.getMe()
        .then((res) => {
          setUser(res.data);
          localStorage.setItem('user', JSON.stringify(res.data));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return userData;
  };

  const loginWithMicrosoft = async (data) => {
    const response = await authAPI.loginWithMicrosoft({
      email: data.email,
      full_name: data.name,
      microsoft_token: data.microsoftToken,
    });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return userData;
  };

  const register = async (data) => {
    const response = await authAPI.register(data);
    const { access_token, user: userData } = response.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return userData;
  };

  const registerWithMicrosoft = async (data) => {
    const response = await authAPI.registerWithMicrosoft({
      full_name: data.full_name,
      email: data.email,
      microsoft_token: data.microsoftToken,
      role: data.role,
    });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return userData;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const isAuthenticated = !!user;
  const isStudent = user?.role === 'student';
  const isStaff = user?.role === 'staff';
  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      loginWithMicrosoft,
      register,
      registerWithMicrosoft,
      logout,
      isAuthenticated,
      isStudent,
      isStaff,
      isAdmin,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
