import { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { recommendationAPI } from '@/lib/api';
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
import { ArrowLeft, CalendarIcon, Loader2, Send, Award, Plus, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function EditRecommendation() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [neededByDate, setNeededByDate] = useState(null);
  
  // Year ranges for attendance
  const [yearsAttended, setYearsAttended] = useState([{ from_year: '', to_year: '' }]);
  
  const [formData, setFormData] = useState({
    first_name: '',
    middle_name: '',
    last_name: '',
    email: user?.email || '',
    phone_number: '',
    address: '',
    enrollment_status: '',
    last_form_class: '',
    co_curricular_activities: '',
    institution_name: '',
    institution_address: '',
    directed_to: '',
    program_name: '',
    collection_method: '',
    delivery_address: '',
  });
  useEffect(() => {
    fetchRecommendation();
  }, [id]);

  const fetchRecommendation = async () => {
    try {
      const res = await recommendationAPI.getById(id);
      const data = res.data;
      
      if (data.status !== 'Pending') {
        toast.error('Only pending recommendations can be edited');
        navigate(`/student/recommendation/${id}`);
        return;
      }

      setFormData({
        first_name: data.first_name || '',
        middle_name: data.middle_name || '',
        last_name: data.last_name || '',
        email: data.email || '',
        phone_number: data.phone_number || '',
        address: data.address || '',
        enrollment_status: data.enrollment_status || '',
        last_form_class: data.last_form_class || '',
        co_curricular_activities: data.co_curricular_activities || '',
        institution_name: data.institution_name || '',
        institution_address: data.institution_address || '',
        directed_to: data.directed_to || '',
        program_name: data.program_name || '',
        collection_method: data.collection_method || '',
        delivery_address: data.delivery_address || '',
      });

      if (data.years_attended && Array.isArray(data.years_attended) && data.years_attended.length > 0) {
        setYearsAttended(data.years_attended);
      }

      if (data.needed_by_date) {
        setNeededByDate(parseISO(data.needed_by_date));
      }

      setLoading(false);
    } catch (error) {
      toast.error('Failed to load recommendation details');
      navigate('/student');
    }
  };


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSelectChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  // Year range handlers
  const addYearRange = () => {
    setYearsAttended([...yearsAttended, { from_year: '', to_year: '' }]);
  };

  const removeYearRange = (index) => {
    if (yearsAttended.length > 1) {
      setYearsAttended(yearsAttended.filter((_, i) => i !== index));
    }
  };

  const updateYearRange = (index, field, value) => {
    const updated = [...yearsAttended];
    updated[index][field] = value;
    setYearsAttended(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!neededByDate) {
      toast.error('Please select a date by which you need the recommendation letter');
      return;
    }

    // Validate year ranges
    const validYears = yearsAttended.filter(y => y.from_year && y.to_year);
    if (validYears.length === 0) {
      toast.error('Please add at least one year range for attendance');
      return;
    }

    // Validate delivery address if needed
    if (formData.collection_method === 'delivery' && !formData.delivery_address) {
      toast.error('Please enter a delivery address');
      return;
    }

    // Validate required fields
    const requiredFields = [
      'first_name', 'last_name', 'email', 'phone_number', 'address',
      'last_form_class', 'institution_name', 
      'institution_address', 'program_name', 'collection_method'
    ];
    
    for (const field of requiredFields) {
      if (!formData[field]) {
        toast.error(`Please fill in all required fields`);
        return;
      }
    }

    setSaving(true);

    try {
      const data = {
        ...formData,
        years_attended: validYears,
        needed_by_date: format(neededByDate, 'yyyy-MM-dd'),
      };
      
      await recommendationAPI.update(id, data);
      toast.success('Recommendation letter request updated successfully!');
      navigate('/student');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit request');
    } finally {
      setSaving(false);
    }
  };

  // Generate years for dropdowns
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

  const formClasses = [
    '1st Form',
    '2nd Form',
    '3rd Form',
    '4th Form',
    '5th Form',
    'Lower 6th',
    'Upper 6th',
  ];

  return (
    <div className="min-h-screen bg-stone-50" data-testid="new-recommendation-page">
      {/* Header */}
      <header className="bg-white border-b border-stone-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <Link to="/student/recommendation/{id}" className="flex items-center gap-2 text-stone-600 hover:text-maroon-500">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Detail</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gold-500" />
          </div>
        ) : (
          <>
            <div className="mb-8 flex items-center gap-4">
              <div className="w-12 h-12 bg-gold-100 rounded-full flex items-center justify-center">
                <Award className="h-6 w-6 text-gold-600" />
              </div>
              <div>
                <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-900">
                  Edit Recommendation Letter Request
                </h1>
                <p className="text-stone-600">Update your recommendation letter request details</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} data-testid="recommendation-request-form">
          {/* Personal Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Personal Information</CardTitle>
              <CardDescription>Enter your full name as it should appear on the letter</CardDescription>
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
                    placeholder="John"
                    data-testid="first-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="middle_name">Middle Name</Label>
                  <Input
                    id="middle_name"
                    name="middle_name"
                    value={formData.middle_name}
                    onChange={handleChange}
                    placeholder="Michael"
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
                    placeholder="Doe"
                    data-testid="last-name-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="your@email.com"
                    data-testid="email-input"
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
                    placeholder="+1 876 XXX XXXX"
                    data-testid="phone-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">Your Address *</Label>
                <Textarea
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  required
                  placeholder="Enter your full residential address"
                  rows={2}
                  data-testid="address-input"
                />
              </div>
            </CardContent>
          </Card>

          {/* School History */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Wolmer's School History</CardTitle>
              <CardDescription>Provide details about your time at Wolmer's Boys' School</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Years Attended - Multiple Ranges */}
              <div className="space-y-3">
                <Label>Years Attended *</Label>
                {yearsAttended.map((yearRange, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="flex-1 grid grid-cols-2 gap-3">
                      <Select 
                        value={yearRange.from_year} 
                        onValueChange={(value) => updateYearRange(index, 'from_year', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="From Year" />
                        </SelectTrigger>
                        <SelectContent>
                          {years.map((year) => (
                            <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Select 
                        value={yearRange.to_year} 
                        onValueChange={(value) => updateYearRange(index, 'to_year', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="To Year" />
                        </SelectTrigger>
                        <SelectContent>
                          {years.map((year) => (
                            <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    {yearsAttended.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeYearRange(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addYearRange}
                  className="mt-2"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Another Year Range
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_form_class">Last Form Class *</Label>
                <Input
                  id="last_form_class"
                  name="last_form_class"
                  value={formData.last_form_class}
                  onChange={handleChange}
                  required
                  placeholder="E.g., Upper 6th, Lower 6th, 5th Form"
                  data-testid="last-form-class-input"
                />
              </div>

              {/* Co-curricular Activities */}
              <div className="space-y-2">
                <Label htmlFor="co_curricular_activities">Positions of Responsibility / Co-curricular Activities</Label>
                <Textarea
                  id="co_curricular_activities"
                  name="co_curricular_activities"
                  value={formData.co_curricular_activities}
                  onChange={handleChange}
                  placeholder="E.g., Head Boy, Prefect, Captain of Football Team, Member of Debate Club, etc."
                  rows={3}
                />
                <p className="text-xs text-stone-500">
                  List any leadership positions, clubs, teams, or activities you participated in
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Institution Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Destination Institution</CardTitle>
              <CardDescription>Where should the recommendation letter be sent?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="institution_name">Institution Name *</Label>
                <Input
                  id="institution_name"
                  name="institution_name"
                  value={formData.institution_name}
                  onChange={handleChange}
                  required
                  placeholder="e.g., University of the West Indies"
                  data-testid="institution-name-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="institution_address">Institution Full Address *</Label>
                <Textarea
                  id="institution_address"
                  name="institution_address"
                  value={formData.institution_address}
                  onChange={handleChange}
                  required
                  placeholder="Enter the complete address including city and country"
                  rows={3}
                  data-testid="institution-address-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="directed_to">Whom Should the Letter Be Directed To?</Label>
                <Input
                  id="directed_to"
                  name="directed_to"
                  value={formData.directed_to}
                  onChange={handleChange}
                  placeholder="e.g., Admissions Committee, Dr. Smith (if applicable)"
                  data-testid="directed-to-input"
                />
                <p className="text-xs text-stone-500">Leave blank if not applicable</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="program_name">Program Name *</Label>
                <Input
                  id="program_name"
                  name="program_name"
                  value={formData.program_name}
                  onChange={handleChange}
                  required
                  placeholder="e.g., Bachelor of Science in Computer Science"
                  data-testid="program-name-input"
                />
              </div>
            </CardContent>
          </Card>

          {/* Request Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Request Details</CardTitle>
              <CardDescription>When do you need the letter and how should we deliver it?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
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
                        data-testid="date-picker-trigger"
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
                  <Label htmlFor="collection_method">Method of Collection *</Label>
                  <Select 
                    value={formData.collection_method} 
                    onValueChange={(value) => handleSelectChange('collection_method', value)}
                  >
                    <SelectTrigger data-testid="collection-method-select">
                      <SelectValue placeholder="Select method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pickup">Picked Up at School</SelectItem>
                      <SelectItem value="emailed">Emailed to Institution</SelectItem>
                      <SelectItem value="delivery">Physical Delivery to Address</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Delivery Address - Show when physical delivery is selected */}
              {formData.collection_method === 'delivery' && (
                <div className="space-y-2">
                  <Label htmlFor="delivery_address">Delivery Address *</Label>
                  <Textarea
                    id="delivery_address"
                    name="delivery_address"
                    value={formData.delivery_address}
                    onChange={handleChange}
                    required
                    placeholder="Enter the complete delivery address"
                    rows={3}
                    data-testid="delivery-address-input"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Link to="/student/recommendation/{id}">
              <Button type="button" variant="outline">Cancel</Button>
            </Link>
            <Button 
              type="submit" 
              disabled={saving || loading}
              className="bg-gold-500 hover:bg-gold-600 text-stone-900"
              data-testid="submit-request-btn"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Update Request
                </>
              )}
            </Button>
          </div>
        </form>
          </>
        )}
      </main>
    </div>
  );
}
