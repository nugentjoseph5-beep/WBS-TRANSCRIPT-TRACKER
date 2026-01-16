import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { requestAPI, notificationAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, getStatusBadgeClass } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  Bell, LogOut, Plus, FileText, Clock, CheckCircle, 
  XCircle, ChevronRight, Menu, X 
} from 'lucide-react';

export default function StudentDashboard() {
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
    inProgress: requests.filter(r => ['In Progress', 'Processing', 'Ready'].includes(r.status)).length,
    completed: requests.filter(r => r.status === 'Completed').length,
  };

  return (
    <div className="min-h-screen bg-stone-50" data-testid="student-dashboard">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/student" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-maroon-500 flex items-center justify-center">
                <span className="font-heading text-gold-500 font-bold">W</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="font-heading text-stone-900 font-semibold">Wolmer's</h1>
                <p className="text-stone-500 text-xs">Transcript Tracker</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Link to="/student" className="text-maroon-500 font-medium">
                My Requests
              </Link>
              <Link to="/student/new-request" className="text-stone-600 hover:text-stone-900">
                New Request
              </Link>
              <Link to="/student/notifications" className="relative text-stone-600 hover:text-stone-900">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center notification-pulse">
                    {unreadCount}
                  </span>
                )}
              </Link>
            </nav>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="hidden md:block text-right">
                <p className="text-sm font-medium text-stone-900">{user?.full_name}</p>
                <p className="text-xs text-stone-500">Student</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="hidden md:flex text-stone-600 hover:text-maroon-500"
                data-testid="logout-btn"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>

              {/* Mobile menu button */}
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
                to="/student" 
                className="block px-3 py-2 rounded-md text-maroon-500 font-medium bg-maroon-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                My Requests
              </Link>
              <Link 
                to="/student/new-request" 
                className="block px-3 py-2 rounded-md text-stone-600 hover:bg-stone-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                New Request
              </Link>
              <Link 
                to="/student/notifications" 
                className="flex items-center justify-between px-3 py-2 rounded-md text-stone-600 hover:bg-stone-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span>Notifications</span>
                {unreadCount > 0 && (
                  <Badge variant="destructive" className="bg-red-500">{unreadCount}</Badge>
                )}
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
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h2>
          <p className="text-stone-600">Track and manage your transcript requests</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-stone-500">Total Requests</p>
                  <p className="text-2xl font-bold text-stone-900">{stats.total}</p>
                </div>
                <FileText className="h-8 w-8 text-maroon-500/20" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-stone-500">Pending</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-500/20" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-stone-500">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.inProgress}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-500/20" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-stone-500">Completed</p>
                  <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500/20" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* New Request Button */}
        <div className="mb-8">
          <Link to="/student/new-request">
            <Button className="bg-maroon-500 hover:bg-maroon-600 text-white" data-testid="new-request-btn">
              <Plus className="h-4 w-4 mr-2" />
              New Transcript Request
            </Button>
          </Link>
        </div>

        {/* Requests List */}
        <Card className="bg-white">
          <CardHeader className="border-b border-stone-100">
            <CardTitle className="font-heading text-xl">My Requests</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-maroon-500 mx-auto"></div>
                <p className="text-stone-500 mt-4">Loading requests...</p>
              </div>
            ) : requests.length === 0 ? (
              <div className="p-8 text-center">
                <FileText className="h-12 w-12 text-stone-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-stone-900 mb-2">No requests yet</h3>
                <p className="text-stone-500 mb-4">Start by creating your first transcript request</p>
                <Link to="/student/new-request">
                  <Button className="bg-maroon-500 hover:bg-maroon-600">
                    <Plus className="h-4 w-4 mr-2" />
                    New Request
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-stone-100">
                {requests.map((request) => (
                  <Link
                    key={request.id}
                    to={`/student/request/${request.id}`}
                    className="flex items-center justify-between p-4 hover:bg-stone-50 transition-colors"
                    data-testid={`request-item-${request.id}`}
                  >
                    <div className="flex items-center gap-4">
                      {getStatusIcon(request.status)}
                      <div>
                        <p className="font-medium text-stone-900">
                          {request.first_name} {request.last_name} - {request.academic_year}
                        </p>
                        <p className="text-sm text-stone-500">
                          Submitted {formatDate(request.created_at)} • {request.collection_method}
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
