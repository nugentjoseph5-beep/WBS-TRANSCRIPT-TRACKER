import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { analyticsAPI, requestAPI, notificationAPI } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatDate, getStatusBadgeClass } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { 
  LayoutDashboard, FileText, Users, Bell, LogOut, Menu, X,
  Clock, CheckCircle, AlertCircle, XCircle, TrendingUp, AlertTriangle, UserCheck, Award
} from 'lucide-react';

const COLORS = ['#800000', '#FFD700', '#78716C', '#22c55e', '#3b82f6', '#ef4444'];
const WORKLOAD_COLORS = ['#800000', '#3b82f6', '#22c55e', '#f97316', '#8b5cf6', '#06b6d4', '#78716c'];

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [analytics, setAnalytics] = useState(null);
  const [recentRequests, setRecentRequests] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [analyticsRes, requestsRes, unreadRes] = await Promise.all([
        analyticsAPI.get(),
        requestAPI.getAllRequests(),
        notificationAPI.getUnreadCount(),
      ]);
      setAnalytics(analyticsRes.data);
      setRecentRequests(requestsRes.data.slice(0, 5));
      setUnreadCount(unreadRes.data.count);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Navigate to requests with filter
  const handleTileClick = (filter) => {
    navigate(`/admin/requests?filter=${filter}`);
  };

  const navItems = [
    { path: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/requests', icon: FileText, label: 'Transcripts' },
    { path: '/admin/recommendations', icon: Award, label: 'Recommendations' },
    { path: '/admin/users', icon: Users, label: 'Users' },
  ];

  const statusData = analytics ? [
    { name: 'Pending', value: analytics.pending_requests, color: '#eab308' },
    { name: 'In Progress', value: analytics.in_progress_requests, color: '#3b82f6' },
    { name: 'Processing', value: analytics.processing_requests, color: '#8b5cf6' },
    { name: 'Ready', value: analytics.ready_requests, color: '#06b6d4' },
    { name: 'Completed', value: analytics.completed_requests, color: '#22c55e' },
    { name: 'Rejected', value: analytics.rejected_requests, color: '#ef4444' },
  ].filter(item => item.value > 0) : [];

  const staffWorkloadData = analytics?.staff_workload || [];
  const overdueByDaysData = analytics?.overdue_by_days || [];

  return (
    <div className="flex h-screen bg-stone-50" data-testid="admin-dashboard">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-stone-900 text-stone-300 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-stone-800">
            <div className="flex items-center gap-3">
              <img 
                src="https://customer-assets.emergentagent.com/job_13afcd2c-9b31-4868-9eb9-1450f0dbe963/artifacts/iuukr0xo_Wolmer%27s_Schools.png" 
                alt="Wolmer's Boys' School Crest" 
                className="w-10 h-10 object-contain"
              />
              <div>
                <h1 className="font-heading text-white font-semibold">Wolmer's</h1>
                <p className="text-stone-500 text-xs">Admin Portal</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-gold-500/20 text-gold-500 border-l-4 border-gold-500 -ml-1' 
                      : 'hover:bg-stone-800 text-stone-400 hover:text-white'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Info */}
          <div className="p-4 border-t border-stone-800">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-maroon-500 flex items-center justify-center">
                <span className="text-white font-medium">
                  {user?.full_name?.charAt(0)}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{user?.full_name}</p>
                <p className="text-stone-500 text-xs truncate">{user?.email}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start text-stone-400 hover:text-white hover:bg-stone-800"
              onClick={handleLogout}
              data-testid="admin-logout-btn"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-stone-200 px-4 md:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                className="md:hidden p-2 -ml-2"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
              <div>
                <h1 className="font-heading text-xl md:text-2xl font-bold text-stone-900">Dashboard</h1>
                <p className="text-stone-500 text-sm hidden md:block">Overview of transcript requests</p>
              </div>
            </div>
            <Link to="/admin/notifications" className="relative" data-testid="admin-notifications-btn">
              <Bell className="h-6 w-6 text-stone-500 cursor-pointer hover:text-stone-700" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </Link>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-maroon-500"></div>
            </div>
          ) : (
            <>
              {/* Stats Cards - Now Clickable */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
                <Card 
                  className="cursor-pointer hover:shadow-lg transition-shadow hover:border-maroon-300"
                  onClick={() => handleTileClick('all')}
                  data-testid="tile-total"
                >
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500">Total Requests</p>
                        <p className="text-2xl md:text-3xl font-bold text-stone-900">{analytics?.total_requests || 0}</p>
                      </div>
                      <FileText className="h-8 w-8 md:h-10 md:w-10 text-maroon-500/20" />
                    </div>
                  </CardContent>
                </Card>
                <Card 
                  className="cursor-pointer hover:shadow-lg transition-shadow hover:border-yellow-300"
                  onClick={() => handleTileClick('Pending')}
                  data-testid="tile-pending"
                >
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500">Pending</p>
                        <p className="text-2xl md:text-3xl font-bold text-yellow-600">{analytics?.pending_requests || 0}</p>
                      </div>
                      <Clock className="h-8 w-8 md:h-10 md:w-10 text-yellow-500/20" />
                    </div>
                  </CardContent>
                </Card>
                <Card 
                  className="cursor-pointer hover:shadow-lg transition-shadow hover:border-green-300"
                  onClick={() => handleTileClick('Completed')}
                  data-testid="tile-completed"
                >
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500">Completed</p>
                        <p className="text-2xl md:text-3xl font-bold text-green-600">{analytics?.completed_requests || 0}</p>
                      </div>
                      <CheckCircle className="h-8 w-8 md:h-10 md:w-10 text-green-500/20" />
                    </div>
                  </CardContent>
                </Card>
                <Card 
                  className="cursor-pointer hover:shadow-lg transition-shadow hover:border-red-300"
                  onClick={() => handleTileClick('Rejected')}
                  data-testid="tile-rejected"
                >
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500">Rejected</p>
                        <p className="text-2xl md:text-3xl font-bold text-red-600">{analytics?.rejected_requests || 0}</p>
                      </div>
                      <XCircle className="h-8 w-8 md:h-10 md:w-10 text-red-500/20" />
                    </div>
                  </CardContent>
                </Card>
                <Card 
                  className={`cursor-pointer hover:shadow-lg transition-shadow col-span-2 md:col-span-1 ${analytics?.overdue_requests > 0 ? 'border-orange-400 bg-orange-50' : ''}`}
                  onClick={() => handleTileClick('overdue')}
                  data-testid="tile-overdue"
                >
                  <CardContent className="p-4 md:p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500">Overdue</p>
                        <p className={`text-2xl md:text-3xl font-bold ${analytics?.overdue_requests > 0 ? 'text-orange-600' : 'text-stone-400'}`}>
                          {analytics?.overdue_requests || 0}
                        </p>
                      </div>
                      <AlertTriangle className={`h-8 w-8 md:h-10 md:w-10 ${analytics?.overdue_requests > 0 ? 'text-orange-500/40' : 'text-stone-300/20'}`} />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Status Distribution Pie Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg">Request Status Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {statusData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={statusData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={2}
                            dataKey="value"
                          >
                            {statusData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center text-stone-400">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Staff Workload Bar Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg flex items-center gap-2">
                      <UserCheck className="h-5 w-5 text-maroon-500" />
                      Staff Workload
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {staffWorkloadData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={staffWorkloadData} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                          <XAxis type="number" tick={{ fontSize: 12 }} />
                          <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={100} />
                          <Tooltip />
                          <Bar dataKey="requests" fill="#800000" radius={[0, 4, 4, 0]}>
                            {staffWorkloadData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.name === 'Unassigned' ? '#78716c' : WORKLOAD_COLORS[index % WORKLOAD_COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center text-stone-400">
                        No assigned requests yet
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Charts Row 2 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Monthly Trend Bar Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-maroon-500" />
                      Monthly Requests
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analytics?.requests_by_month?.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={analytics.requests_by_month}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#800000" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center text-stone-400">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Overdue Breakdown Chart */}
                <Card className={overdueByDaysData.length > 0 ? 'border-orange-200' : ''}>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg flex items-center gap-2">
                      <AlertTriangle className={`h-5 w-5 ${overdueByDaysData.length > 0 ? 'text-orange-500' : 'text-stone-400'}`} />
                      Overdue Breakdown
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {overdueByDaysData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={overdueByDaysData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip />
                          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                            {overdueByDaysData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[300px] flex flex-col items-center justify-center text-stone-400">
                        <CheckCircle className="h-12 w-12 text-green-500 mb-2" />
                        <p>No overdue requests!</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Charts Row 3 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Enrollment Status Pie */}
                <Card>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg">By Enrollment Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analytics?.requests_by_enrollment?.some(e => e.value > 0) ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={analytics.requests_by_enrollment}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            dataKey="value"
                            label
                          >
                            {analytics.requests_by_enrollment.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[250px] flex items-center justify-center text-stone-400">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Collection Method Pie */}
                <Card>
                  <CardHeader>
                    <CardTitle className="font-heading text-lg">By Collection Method</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analytics?.requests_by_collection_method?.some(e => e.value > 0) ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={analytics.requests_by_collection_method}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            dataKey="value"
                            label
                          >
                            {analytics.requests_by_collection_method.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-[250px] flex items-center justify-center text-stone-400">
                        No data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Recent Requests */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="font-heading text-lg">Recent Requests</CardTitle>
                  <Link to="/admin/requests">
                    <Button variant="outline" size="sm">View All</Button>
                  </Link>
                </CardHeader>
                <CardContent>
                  {recentRequests.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-stone-200">
                            <th className="text-left py-3 px-4 font-medium text-stone-500">Student</th>
                            <th className="text-left py-3 px-4 font-medium text-stone-500">Academic Year</th>
                            <th className="text-left py-3 px-4 font-medium text-stone-500">Status</th>
                            <th className="text-left py-3 px-4 font-medium text-stone-500">Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recentRequests.map((request) => (
                            <tr 
                              key={request.id} 
                              className="border-b border-stone-100 hover:bg-stone-50 cursor-pointer"
                              onClick={() => navigate(`/admin/request/${request.id}`)}
                            >
                              <td className="py-3 px-4">
                                <p className="font-medium text-stone-900">{request.student_name}</p>
                                <p className="text-xs text-stone-500">{request.student_email}</p>
                              </td>
                              <td className="py-3 px-4 text-stone-600">{request.academic_year}</td>
                              <td className="py-3 px-4">
                                <span className={getStatusBadgeClass(request.status)}>
                                  {request.status}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-stone-500">{formatDate(request.created_at)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="py-8 text-center text-stone-400">
                      No requests yet
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
