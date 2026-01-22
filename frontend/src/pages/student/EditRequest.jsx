import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { requestAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';
import { ArrowLeft, CalendarIcon, Loader2, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function EditRequest() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [neededByDate, setNeededByDate] = useState(null);
  const [request, setRequest] = useState(null);
  
  const [formData, setFormData] = useState({
    first_name: '',
    middle_name: '',
    last_name: '',
    school_id: '',
    enrollment_status: '',
    academic_year: '',
    wolmers_email: '',
    personal_email: '',
    phone_number: '',
    last_form_class: '',
    reason: '',
    collection_method: '',
    institution_name: '',
    institution_address: '',
    institution_phone: '',
    institution_email: '',
  });

  useEffect(() => {
    fetchRequest();
  }, [id]);

  const fetchRequest = async () => {
    try {
      const res = await requestAPI.getById(id);
      const data = res.data;
      
      // Check if request can be edited
      if (data.status !== 'Pending') {
        toast.error(`This request cannot be edited because its status is '${data.status}'. Only pending requests can be modified.`);
        navigate(`/student/request/${id}`);
        return;
      }
      
      setRequest(data);
      setFormData({
        first_name: data.first_name || '',
        middle_name: data.middle_name || '',
        last_name: data.last_name || '',
        school_id: data.school_id || '',
        enrollment_status: data.enrollment_status || '',
        academic_year: data.academic_year || '',
        wolmers_email: data.wolmers_email || '',
        personal_email: data.personal_email || '',
        phone_number: data.phone_number || '',
        last_form_class: data.last_form_class || '',
        reason: data.reason || '',
        collection_method: data.collection_method || '',
        institution_name: data.institution_name || '',
        institution_address: data.institution_address || '',
        institution_phone: data.institution_phone || '',
        institution_email: data.institution_email || '',
      });
      
      if (data.needed_by_date) {
        setNeededByDate(parseISO(data.needed_by_date));
      }
    } catch (error) {
      toast.error('Failed to load request');
      navigate('/student');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSelectChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!neededByDate) {
      toast.error('Please select a date by which you need the transcript');
      return;
    }

    setSaving(true);

    try {
      const data = {
        ...formData,
        needed_by_date: format(neededByDate, 'yyyy-MM-dd'),
      };
      
      await requestAPI.editAsStudent(id, data);
      toast.success('Request updated successfully!');
      navigate(`/student/request/${id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update request');
    } finally {
      setSaving(false);
    }
  };

  const currentYear = new Date().getFullYear();
  const academicYears = [];
  for (let i = currentYear; i >= currentYear - 20; i--) {
    academicYears.push(`${i}-${i + 1}`);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-maroon-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50" data-testid="edit-request-page">
      {/* Header */}
      <header className="bg-white border-b border-stone-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <Link to={`/student/request/${id}`} className="flex items-center gap-2 text-stone-600 hover:text-maroon-500">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Request</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-900 mb-2">
            Edit Transcript Request
          </h1>
          <p className="text-stone-600">Update your request details below</p>
        </div>

        <form onSubmit={handleSubmit} data-testid="edit-request-form">
          {/* Personal Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Personal Information</CardTitle>
              <CardDescription>Enter your name as it appears on official records</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name *</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                    data-testid="edit-first-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="middle_name">Middle Name</Label>
                  <Input
                    id="middle_name"
                    name="middle_name"
                    value={formData.middle_name}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name *</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                    data-testid="edit-last-name"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="school_id">School ID Number *</Label>
                  <Input
                    id="school_id"
                    name="school_id"
                    value={formData.school_id}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="enrollment_status">Enrollment Status *</Label>
                  <Select 
                    value={formData.enrollment_status} 
                    onValueChange={(value) => handleSelectChange('enrollment_status', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="enrolled">Currently Enrolled</SelectItem>
                      <SelectItem value="graduate">Graduate</SelectItem>
                      <SelectItem value="withdrawn">Withdrawn</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="academic_year">Academic Year for Transcript *</Label>
                <Select 
                  value={formData.academic_year} 
                  onValueChange={(value) => handleSelectChange('academic_year', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select academic year" />
                  </SelectTrigger>
                  <SelectContent>
                    {academicYears.map((year) => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="wolmers_email">Wolmer's Email *</Label>
                <Input
                  id="wolmers_email"
                  name="wolmers_email"
                  type="email"
                  value={formData.wolmers_email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="personal_email">Personal Email *</Label>
                  <Input
                    id="personal_email"
                    name="personal_email"
                    type="email"
                    value={formData.personal_email}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone_number">Phone Number *</Label>
                  <Input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={formData.phone_number}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Request Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Request Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reason">Reason for Request *</Label>
                <Textarea
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleChange}
                  required
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Date Needed By *</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !neededByDate && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {neededByDate ? format(neededByDate, "PPP") : "Select date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={neededByDate}
                        onSelect={setNeededByDate}
                        disabled={(date) => date < new Date()}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="collection_method">Collection Method *</Label>
                  <Select 
                    value={formData.collection_method} 
                    onValueChange={(value) => handleSelectChange('collection_method', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pickup">Pickup at Bursary</SelectItem>
                      <SelectItem value="emailed">Emailed to Institution</SelectItem>
                      <SelectItem value="delivery">Physical Delivery to Address</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Institution Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Institution Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="institution_name">
                  Institution Name {(formData.collection_method === 'emailed' || formData.collection_method === 'delivery') && '*'}
                </Label>
                <Input
                  id="institution_name"
                  name="institution_name"
                  value={formData.institution_name}
                  onChange={handleChange}
                  required={formData.collection_method === 'emailed' || formData.collection_method === 'delivery'}
                  placeholder="e.g., University of the West Indies"
                />
              </div>

              {formData.collection_method === 'delivery' && (
                <div className="space-y-2">
                  <Label htmlFor="institution_address">Institution Address *</Label>
                  <Textarea
                    id="institution_address"
                    name="institution_address"
                    value={formData.institution_address}
                    onChange={handleChange}
                    required
                    rows={3}
                  />
                </div>
              )}

              {(formData.collection_method === 'emailed' || formData.collection_method === 'delivery') && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="institution_phone">Institution Phone</Label>
                    <Input
                      id="institution_phone"
                      name="institution_phone"
                      type="tel"
                      value={formData.institution_phone}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="institution_email">
                      Institution Email {formData.collection_method === 'emailed' && '*'}
                    </Label>
                    <Input
                      id="institution_email"
                      name="institution_email"
                      type="email"
                      value={formData.institution_email}
                      onChange={handleChange}
                      required={formData.collection_method === 'emailed'}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Link to={`/student/request/${id}`}>
              <Button type="button" variant="outline">Cancel</Button>
            </Link>
            <Button 
              type="submit" 
              disabled={saving}
              className="bg-maroon-500 hover:bg-maroon-600"
              data-testid="save-changes-btn"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
