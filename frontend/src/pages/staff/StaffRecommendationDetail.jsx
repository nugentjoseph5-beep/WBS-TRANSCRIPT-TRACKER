import { useState, useEffect, useRef } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { recommendationAPI } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { formatDate, formatDateTime, getStatusBadgeClass } from '@/lib/utils';
import { toast } from 'sonner';
import { 
  ArrowLeft, FileText, User, Mail, Phone, MapPin, 
  Calendar, Clock, Building, Download, Upload,
  XCircle, Loader2, Award, Plus
} from 'lucide-react';

export default function StaffRecommendationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileInputRef = useRef(null);
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [statusUpdateDialogOpen, setStatusUpdateDialogOpen] = useState(false);
  const [pendingStatus, setPendingStatus] = useState('');
  const [statusNote, setStatusNote] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [staffNotes, setStaffNotes] = useState('');
  const [coActivitiesEdit, setCoActivitiesEdit] = useState(false);
  const [coActivitiesValue, setCoActivitiesValue] = useState('');

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const res = await recommendationAPI.getById(id);
      setRequest(res.data);
      setStaffNotes(res.data.staff_notes || '');
      setCoActivitiesValue(res.data.co_curricular_activities || '');
    } catch (error) {
      toast.error('Failed to load request details');
      navigate('/staff');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    // Prompt for note before updating status
    setPendingStatus(newStatus);
    setStatusNote('');
    setStatusUpdateDialogOpen(true);
  };

  const confirmStatusUpdate = async () => {
    if (!statusNote.trim()) {
      toast.error('Please provide a note for the status change');
      return;
    }

    setUpdating(true);
    try {
      await recommendationAPI.update(id, { 
        status: pendingStatus,
        note: statusNote 
      });
      toast.success(`Status updated to ${pendingStatus}`);
      setStatusUpdateDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleSaveNotes = async () => {
    setUpdating(true);
    try {
      await recommendationAPI.update(id, { staff_notes: staffNotes });
      toast.success('Notes saved successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to save notes');
    } finally {
      setUpdating(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }

    setUpdating(true);
    try {
      await recommendationAPI.update(id, { rejection_reason: rejectionReason });
      toast.success('Request rejected');
      setRejectDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Failed to reject request');
    } finally {
      setUpdating(false);
    }
  };

  const handleSaveCoActivities = async () => {
    setUpdating(true);
    try {
      await recommendationAPI.update(id, { co_curricular_activities: coActivitiesValue });
      toast.success('Co-curricular activities updated successfully');
      setCoActivitiesEdit(false);
      fetchData();
    } catch (error) {
      toast.error('Failed to update co-curricular activities');
    } finally {
      setUpdating(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await recommendationAPI.uploadDocument(id, file);
      toast.success('Document uploaded successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to upload document');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDownloadDocument = async (doc) => {
    try {
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/documents/${doc.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await res.json();
      const blob = atob(data.content);
      const byteArray = new Uint8Array(blob.length);
      for (let i = 0; i < blob.length; i++) {
        byteArray[i] = blob.charCodeAt(i);
      }
      const file = new Blob([byteArray], { type: data.content_type });
      const url = URL.createObjectURL(file);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Failed to download document');
    }
  };

  const statusOrder = ['Pending', 'In Progress', 'Processing', 'Ready', 'Completed'];

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold-500"></div>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-stone-900">Request not found</h2>
          <Link to="/staff" className="text-gold-500 hover:underline mt-2 block">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50" data-testid="staff-recommendation-detail">
      {/* Header */}
      <header className="bg-white border-b border-stone-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/staff" className="flex items-center gap-2 text-stone-600 hover:text-gold-500">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Dashboard</span>
            </Link>
            <span className={getStatusBadgeClass(request.status)}>
              {request.status}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title */}
        <div className="mb-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-gold-100 rounded-full flex items-center justify-center">
            <Award className="h-6 w-6 text-gold-600" />
          </div>
          <div>
            <h1 className="font-heading text-2xl font-bold text-stone-900">
              Recommendation Letter Request
            </h1>
            <p className="text-stone-500">
              Submitted {formatDate(request.created_at)} by {request.student_name}
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Student Information */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <User className="h-5 w-5 text-gold-500" />
                  Student Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-stone-500">Full Name</p>
                    <p className="font-medium">{request.first_name} {request.middle_name} {request.last_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-stone-500">Email</p>
                    <p className="font-medium flex items-center gap-1">
                      <Mail className="h-4 w-4 text-stone-400" />
                      {request.email}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-stone-500">Phone</p>
                    <p className="font-medium flex items-center gap-1">
                      <Phone className="h-4 w-4 text-stone-400" />
                      {request.phone_number}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-stone-500">Address</p>
                    <p className="font-medium flex items-center gap-1">
                      <MapPin className="h-4 w-4 text-stone-400" />
                      {request.address}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* School History */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <Building className="h-5 w-5 text-gold-500" />
                  Wolmer's School History
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-stone-500">Years Attended</p>
                    <p className="font-medium">
                      {Array.isArray(request.years_attended) 
                        ? request.years_attended.map(y => `${y.from_year}-${y.to_year}`).join(', ')
                        : request.years_attended_str || request.years_attended || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-stone-500">Last Form Class</p>
                    <p className="font-medium">{request.last_form_class}</p>
                  </div>
                </div>
                {request.co_curricular_activities && (
                  <div className="mt-4">
                    <p className="text-sm text-stone-500">Positions of Responsibility / Co-curricular Activities</p>
                    <p className="font-medium whitespace-pre-wrap">{request.co_curricular_activities}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Institution Details */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <Building className="h-5 w-5 text-gold-500" />
                  Destination Institution
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-stone-500">Institution Name</p>
                  <p className="font-medium">{request.institution_name}</p>
                </div>
                <div>
                  <p className="text-sm text-stone-500">Institution Address</p>
                  <p className="font-medium">{request.institution_address}</p>
                </div>
                {request.directed_to && (
                  <div>
                    <p className="text-sm text-stone-500">Letter Directed To</p>
                    <p className="font-medium">{request.directed_to}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-stone-500">Program Name</p>
                  <p className="font-medium">{request.program_name}</p>
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-stone-500">Needed By</p>
                    <p className="font-medium flex items-center gap-1">
                      <Calendar className="h-4 w-4 text-stone-400" />
                      {formatDate(request.needed_by_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-stone-500">Collection Method</p>
                    <p className="font-medium">
                      {request.collection_method === 'pickup' ? 'Pickup at School' : 'Emailed to Institution'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Documents */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-gold-500" />
                    Documents
                  </span>
                  <div>
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      className="hidden"
                      accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                    >
                      {uploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Upload className="h-4 w-4 mr-2" />
                          Upload
                        </>
                      )}
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {request.documents?.length === 0 ? (
                  <p className="text-stone-500 text-sm">No documents uploaded yet</p>
                ) : (
                  <div className="space-y-2">
                    {request.documents?.map((doc) => (
                      <div 
                        key={doc.id}
                        className="flex items-center justify-between p-3 bg-stone-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-stone-400" />
                          <div>
                            <p className="font-medium text-sm">{doc.filename}</p>
                            <p className="text-xs text-stone-500">
                              Uploaded by {doc.uploaded_by} • {formatDate(doc.uploaded_at)}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadDocument(doc)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions */}
            {request.status !== 'Rejected' && request.status !== 'Completed' && (
              <Card>
                <CardHeader>
                  <CardTitle className="font-heading text-lg">Update Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    {statusOrder.map((status) => (
                      <Button
                        key={status}
                        variant={request.status === status ? 'default' : 'outline'}
                        size="sm"
                        disabled={updating || request.status === status}
                        onClick={() => handleStatusUpdate(status)}
                        className={request.status === status ? 'bg-gold-500 text-stone-900' : ''}
                      >
                        {status}
                      </Button>
                    ))}
                  </div>
                  
                  <Button
                    variant="destructive"
                    className="w-full"
                    onClick={() => setRejectDialogOpen(true)}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Reject Request
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Staff Notes */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg">Staff Notes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  value={staffNotes}
                  onChange={(e) => setStaffNotes(e.target.value)}
                  placeholder="Add internal notes about this request..."
                  rows={4}
                />
                <Button
                  onClick={handleSaveNotes}
                  disabled={updating}
                  className="w-full bg-gold-500 hover:bg-gold-600 text-stone-900"
                >
                  {updating ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  Save Notes
                </Button>
              </CardContent>
            </Card>

            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <Clock className="h-5 w-5 text-gold-500" />
                  Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {request.timeline?.map((entry, index) => (
                    <div key={index} className="relative pl-6 pb-4 border-l-2 border-stone-200 last:border-l-0 last:pb-0">
                      <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-gold-500"></div>
                      <div>
                        <p className="font-medium text-sm">{entry.status}</p>
                        <p className="text-xs text-stone-500">{entry.note}</p>
                        <p className="text-xs text-stone-400 mt-1">
                          {formatDateTime(entry.timestamp)} • {entry.updated_by}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Rejection Reason */}
            {request.status === 'Rejected' && request.rejection_reason && (
              <Card className="border-red-200 bg-red-50">
                <CardHeader>
                  <CardTitle className="font-heading text-lg text-red-800">
                    Rejection Reason
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-red-700">{request.rejection_reason}</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Request</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="rejection-reason">Reason for Rejection</Label>
            <Textarea
              id="rejection-reason"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Please provide a reason for rejecting this request..."
              className="mt-2"
              rows={4}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              variant="destructive"
              onClick={handleReject}
              disabled={updating}
            >
              {updating ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              Reject Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
