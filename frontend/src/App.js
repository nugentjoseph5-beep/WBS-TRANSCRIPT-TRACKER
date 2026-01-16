import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/lib/auth";
import { Toaster } from "@/components/ui/sonner";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";
import ResetPasswordPage from "@/pages/ResetPasswordPage";
import StudentDashboard from "@/pages/student/StudentDashboard";
import NewRequest from "@/pages/student/NewRequest";
import RequestDetail from "@/pages/student/RequestDetail";
import StudentNotifications from "@/pages/student/StudentNotifications";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import AdminRequests from "@/pages/admin/AdminRequests";
import AdminUsers from "@/pages/admin/AdminUsers";
import StaffDashboard from "@/pages/staff/StaffDashboard";
import StaffRequestDetail from "@/pages/staff/StaffRequestDetail";

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-stone-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-maroon-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to appropriate dashboard based on role
    if (user.role === 'student') return <Navigate to="/student" replace />;
    if (user.role === 'staff') return <Navigate to="/staff" replace />;
    if (user.role === 'admin') return <Navigate to="/admin" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
};

// Public Route - redirect if already logged in
const PublicRoute = ({ children }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-stone-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-maroon-500"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    if (user.role === 'student') return <Navigate to="/student" replace />;
    if (user.role === 'staff') return <Navigate to="/staff" replace />;
    if (user.role === 'admin') return <Navigate to="/admin" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Student Routes */}
      <Route path="/student" element={
        <ProtectedRoute allowedRoles={['student']}>
          <StudentDashboard />
        </ProtectedRoute>
      } />
      <Route path="/student/new-request" element={
        <ProtectedRoute allowedRoles={['student']}>
          <NewRequest />
        </ProtectedRoute>
      } />
      <Route path="/student/request/:id" element={
        <ProtectedRoute allowedRoles={['student']}>
          <RequestDetail />
        </ProtectedRoute>
      } />
      <Route path="/student/notifications" element={
        <ProtectedRoute allowedRoles={['student']}>
          <StudentNotifications />
        </ProtectedRoute>
      } />

      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="/admin/requests" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminRequests />
        </ProtectedRoute>
      } />
      <Route path="/admin/users" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminUsers />
        </ProtectedRoute>
      } />

      {/* Staff Routes */}
      <Route path="/staff" element={
        <ProtectedRoute allowedRoles={['staff']}>
          <StaffDashboard />
        </ProtectedRoute>
      } />
      <Route path="/staff/request/:id" element={
        <ProtectedRoute allowedRoles={['staff']}>
          <StaffRequestDetail />
        </ProtectedRoute>
      } />

      {/* Catch all - redirect to landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
