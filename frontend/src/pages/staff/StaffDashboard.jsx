import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { requestAPI, notificationAPI } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDate, getStatusBadgeClass } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  Bell, LogOut, FileText, Clock, CheckCircle, 
  XCircle, ChevronRight, Menu, X 
} from 'lucide-react';

export default function StaffDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [requestsRes, unreadRes] = await Promise.all([
        requestAPI.getAll(),
        notificationAPI.getUnreadCount(),
      ]);
      setRequests(requestsRes.data);
      setUnreadCount(unreadRes.data.count);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'Rejected':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const stats = {
    total: requests.length,
    pending: requests.filter(r => r.status === 'Pending').length,
    inProgress: requests.filter(r => ['In Progress', 'Processing'].includes(r.status)).length,
    ready: requests.filter(r => r.status === 'Ready').length,
    completed: requests.filter(r => r.status === 'Completed').length,
  };

  return (
    <div className="min-h-screen bg-stone-50" data-testid="staff-dashboard">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/staff" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gold-500 flex items-center justify-center">
                <span className="font-heading text-maroon-900 font-bold">W</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="font-heading text-stone-900 font-semibold">Wolmer's</h1>
                <p className="text-stone-500 text-xs">Staff Portal</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Link to="/staff" className="text-gold-600 font-medium">
                My Assignments
              </Link>
              <div className="relative">
                <Bell className="h-5 w-5 text-stone-500 cursor-pointer hover:text-stone-700" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </div>
            </nav>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="hidden md:block text-right">
                <p className="text-sm font-medium text-stone-900">{user?.full_name}</p>
                <p className="text-xs text-stone-500">Staff</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="hidden md:flex text-stone-600 hover:text-gold-600"
                data-testid="staff-logout-btn"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>

              <button
                className="md:hidden p-2"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-stone-200 bg-white">
            <div className="px-4 py-3 space-y-2">
              <Link 
                to="/staff" 
                className="block px-3 py-2 rounded-md text-gold-600 font-medium bg-gold-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                My Assignments
              </Link>
              <hr className="my-2" />
              <div className="px-3 py-2">
                <p className="text-sm font-medium text-stone-900">{user?.full_name}</p>
                <p className="text-xs text-stone-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-3 py-2 rounded-md text-left text-red-600 hover:bg-red-50"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="font-heading text-2xl md:text-3xl font-bold text-stone-900 mb-2">
            Welcome, {user?.full_name?.split(' ')[0]}!
          </h2>
          <p className="text-stone-600">Manage your assigned transcript requests</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-sm text-stone-500">Assigned</p>
                <p className="text-2xl font-bold text-stone-900">{stats.total}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-sm text-stone-500">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-sm text-stone-500">In Progress</p>
                <p className="text-2xl font-bold text-blue-600">{stats.inProgress}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-sm text-stone-500">Ready</p>
                <p className="text-2xl font-bold text-cyan-600">{stats.ready}</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white col-span-2 md:col-span-1">
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-sm text-stone-500">Completed</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Requests List */}
        <Card className="bg-white">
          <CardHeader className="border-b border-stone-100">
            <CardTitle className="font-heading text-xl">My Assigned Requests</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-500 mx-auto"></div>
                <p className="text-stone-500 mt-4">Loading requests...</p>
              </div>
            ) : requests.length === 0 ? (
              <div className="p-8 text-center">
                <FileText className="h-12 w-12 text-stone-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-stone-900 mb-2">No assignments yet</h3>
                <p className="text-stone-500">You'll see requests here when they're assigned to you</p>
              </div>
            ) : (
              <div className="divide-y divide-stone-100">
                {requests.map((request) => (
                  <Link
                    key={request.id}
                    to={`/staff/request/${request.id}`}
                    className="flex items-center justify-between p-4 hover:bg-stone-50 transition-colors"
                    data-testid={`staff-request-item-${request.id}`}
                  >
                    <div className="flex items-center gap-4">
                      {getStatusIcon(request.status)}
                      <div>
                        <p className="font-medium text-stone-900">
                          {request.first_name} {request.last_name}
                        </p>
                        <p className="text-sm text-stone-500">
                          {request.school_id} • {request.academic_year} • Needed by {formatDate(request.needed_by_date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={getStatusBadgeClass(request.status)}>
                        {request.status}
                      </span>
                      <ChevronRight className="h-5 w-5 text-stone-400" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
