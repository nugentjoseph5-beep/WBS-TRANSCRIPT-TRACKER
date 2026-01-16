import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { requestAPI, userAPI } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { formatDate, getStatusBadgeClass } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  LayoutDashboard, FileText, Users, LogOut, Menu, X,
  Search, Filter, ChevronRight, UserPlus, Loader2
} from 'lucide-react';

export default function AdminRequests() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [staffMembers, setStaffMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [selectedStaff, setSelectedStaff] = useState('');
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterRequests();
  }, [requests, searchTerm, statusFilter]);

  const fetchData = async () => {
    try {
      const [requestsRes, staffRes] = await Promise.all([
        requestAPI.getAllRequests(),
        userAPI.getStaffMembers(),
      ]);
      setRequests(requestsRes.data);
      setStaffMembers(staffRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const filterRequests = () => {
    let filtered = [...requests];

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(r => 
        r.student_name.toLowerCase().includes(term) ||
        r.student_email.toLowerCase().includes(term) ||
        r.school_id.toLowerCase().includes(term)
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(r => r.status === statusFilter);
    }

    setFilteredRequests(filtered);
  };

  const handleAssignStaff = async () => {
    if (!selectedStaff || !selectedRequest) return;

    setAssigning(true);
    try {
      await requestAPI.update(selectedRequest.id, { assigned_staff_id: selectedStaff });
      toast.success('Staff assigned successfully');
      setAssignDialogOpen(false);
      setSelectedRequest(null);
      setSelectedStaff('');
      fetchData();
    } catch (error) {
      toast.error('Failed to assign staff');
    } finally {
      setAssigning(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { path: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/requests', icon: FileText, label: 'Requests' },
    { path: '/admin/users', icon: Users, label: 'Users' },
  ];

  return (
    <div className="flex h-screen bg-stone-50" data-testid="admin-requests-page">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-stone-900 text-stone-300 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-stone-800">
            <Link to="/admin" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gold-500 flex items-center justify-center">
                <span className="font-heading text-maroon-900 font-bold">W</span>
              </div>
              <div>
                <h1 className="font-heading text-white font-semibold">Wolmer's</h1>
                <p className="text-stone-500 text-xs">Admin Portal</p>
              </div>
            </Link>
          </div>

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

          <div className="p-4 border-t border-stone-800">
            <Button
              variant="ghost"
              className="w-full justify-start text-stone-400 hover:text-white hover:bg-stone-800"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-stone-200 px-4 md:px-8 py-4">
          <div className="flex items-center gap-4">
            <button
              className="md:hidden p-2 -ml-2"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
            <div>
              <h1 className="font-heading text-xl md:text-2xl font-bold text-stone-900">All Requests</h1>
              <p className="text-stone-500 text-sm hidden md:block">Manage transcript requests</p>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" />
              <Input
                placeholder="Search by name, email, or school ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="search-input"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48" data-testid="status-filter">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="Pending">Pending</SelectItem>
                <SelectItem value="In Progress">In Progress</SelectItem>
                <SelectItem value="Processing">Processing</SelectItem>
                <SelectItem value="Ready">Ready</SelectItem>
                <SelectItem value="Completed">Completed</SelectItem>
                <SelectItem value="Rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Requests Table */}
          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="p-8 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-maroon-500 mx-auto"></div>
                </div>
              ) : filteredRequests.length === 0 ? (
                <div className="p-8 text-center text-stone-400">
                  {searchTerm || statusFilter !== 'all' ? 'No requests match your filters' : 'No requests yet'}
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-stone-200 bg-stone-50">
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Student</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">School ID</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Year</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Status</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Assigned To</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Date</th>
                        <th className="text-left py-3 px-4 font-medium text-stone-500">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredRequests.map((request) => (
                        <tr 
                          key={request.id} 
                          className="border-b border-stone-100 hover:bg-stone-50"
                          data-testid={`request-row-${request.id}`}
                        >
                          <td className="py-3 px-4">
                            <p className="font-medium text-stone-900">{request.student_name}</p>
                            <p className="text-xs text-stone-500">{request.student_email}</p>
                          </td>
                          <td className="py-3 px-4 text-stone-600">{request.school_id}</td>
                          <td className="py-3 px-4 text-stone-600">{request.academic_year}</td>
                          <td className="py-3 px-4">
                            <span className={getStatusBadgeClass(request.status)}>
                              {request.status}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            {request.assigned_staff_name ? (
                              <div className="flex items-center gap-2">
                                <span className="text-stone-600">{request.assigned_staff_name}</span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0 text-stone-400 hover:text-maroon-500"
                                  onClick={() => {
                                    setSelectedRequest(request);
                                    setSelectedStaff(request.assigned_staff_id || '');
                                    setAssignDialogOpen(true);
                                  }}
                                  data-testid={`reassign-btn-${request.id}`}
                                  title="Reassign"
                                >
                                  <UserPlus className="h-3 w-3" />
                                </Button>
                              </div>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setSelectedRequest(request);
                                  setSelectedStaff('');
                                  setAssignDialogOpen(true);
                                }}
                                data-testid={`assign-btn-${request.id}`}
                              >
                                <UserPlus className="h-4 w-4 mr-1" />
                                Assign
                              </Button>
                            )}
                          </td>
                          <td className="py-3 px-4 text-stone-500">{formatDate(request.created_at)}</td>
                          <td className="py-3 px-4">
                            <Link to={`/staff/request/${request.id}`}>
                              <Button variant="ghost" size="sm">
                                <ChevronRight className="h-4 w-4" />
                              </Button>
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </main>
      </div>

      {/* Assign Staff Dialog */}
      <Dialog open={assignDialogOpen} onOpenChange={setAssignDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-heading">
              {selectedRequest?.assigned_staff_id ? 'Reassign Staff Member' : 'Assign Staff Member'}
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            {selectedRequest?.assigned_staff_name && (
              <p className="text-sm text-stone-500 mb-4">
                Currently assigned to: <strong>{selectedRequest.assigned_staff_name}</strong>
              </p>
            )}
            <Label>Select Staff Member</Label>
            <Select value={selectedStaff} onValueChange={setSelectedStaff}>
              <SelectTrigger className="mt-2" data-testid="staff-select">
                <SelectValue placeholder="Choose a staff member" />
              </SelectTrigger>
              <SelectContent>
                {staffMembers.map((staff) => (
                  <SelectItem key={staff.id} value={staff.id}>
                    {staff.full_name}
                    {staff.id === selectedRequest?.assigned_staff_id && ' (current)'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {staffMembers.length === 0 && (
              <p className="text-sm text-stone-500 mt-2">
                No staff members available. <Link to="/admin/users" className="text-maroon-500 hover:underline">Add staff members</Link>
              </p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssignDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleAssignStaff} 
              disabled={!selectedStaff || assigning}
              className="bg-maroon-500 hover:bg-maroon-600"
              data-testid="confirm-assign-btn"
            >
              {assigning ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Assign
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
