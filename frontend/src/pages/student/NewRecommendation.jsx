import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
import { format } from 'date-fns';
import { ArrowLeft, CalendarIcon, Loader2, Send, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function NewRecommendation() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [neededByDate, setNeededByDate] = useState(null);
  
  const [formData, setFormData] = useState({
    first_name: '',
    middle_name: '',
    last_name: '',
    email: user?.email || '',
    phone_number: '',
    address: '',
    years_attended: '',
    last_form_class: '',
    institution_name: '',
    institution_address: '',
    directed_to: '',
    program_name: '',
    collection_method: '',
  });

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
      toast.error('Please select a date by which you need the recommendation letter');
      return;
    }

    // Validate required fields
    const requiredFields = [
      'first_name', 'last_name', 'email', 'phone_number', 'address',
      'years_attended', 'last_form_class', 'institution_name', 
      'institution_address', 'program_name', 'collection_method'
    ];
    
    for (const field of requiredFields) {
      if (!formData[field]) {
        toast.error(`Please fill in all required fields`);
        return;
      }
    }

    setLoading(true);

    try {
      const data = {
        ...formData,
        needed_by_date: format(neededByDate, 'yyyy-MM-dd'),
      };
      
      await recommendationAPI.create(data);
      toast.success('Recommendation letter request submitted successfully!');
      navigate('/student');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit request');
    } finally {
      setLoading(false);
    }
  };

  // Generate year ranges for years attended
  const currentYear = new Date().getFullYear();
  const yearRanges = [];
  for (let endYear = currentYear; endYear >= currentYear - 30; endYear--) {
    for (let duration = 5; duration <= 7; duration++) {
      const startYear = endYear - duration;
      if (startYear >= 1980) {
        yearRanges.push(`${startYear}-${endYear}`);
      }
    }
  }
  // Remove duplicates and sort
  const uniqueYearRanges = [...new Set(yearRanges)].sort((a, b) => {
    const aEnd = parseInt(a.split('-')[1]);
    const bEnd = parseInt(b.split('-')[1]);
    return bEnd - aEnd;
  });

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
            <Link to="/student/select-service" className="flex items-center gap-2 text-stone-600 hover:text-maroon-500">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Service Selection</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center gap-4">
          <div className="w-12 h-12 bg-gold-100 rounded-full flex items-center justify-center">
            <Award className="h-6 w-6 text-gold-600" />
          </div>
          <div>
            <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-900">
              New Recommendation Letter Request
            </h1>
            <p className="text-stone-600">Fill out the form below to request a letter of recommendation</p>
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="years_attended">Years Attended *</Label>
                  <Select 
                    value={formData.years_attended} 
                    onValueChange={(value) => handleSelectChange('years_attended', value)}
                  >
                    <SelectTrigger data-testid="years-attended-select">
                      <SelectValue placeholder="Select years" />
                    </SelectTrigger>
                    <SelectContent>
                      {uniqueYearRanges.slice(0, 50).map((range) => (
                        <SelectItem key={range} value={range}>{range}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_form_class">Last Form Class *</Label>
                  <Select 
                    value={formData.last_form_class} 
                    onValueChange={(value) => handleSelectChange('last_form_class', value)}
                  >
                    <SelectTrigger data-testid="form-class-select">
                      <SelectValue placeholder="Select form class" />
                    </SelectTrigger>
                    <SelectContent>
                      {formClasses.map((formClass) => (
                        <SelectItem key={formClass} value={formClass}>{formClass}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
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
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Link to="/student/select-service">
              <Button type="button" variant="outline">Cancel</Button>
            </Link>
            <Button 
              type="submit" 
              disabled={loading}
              className="bg-gold-500 hover:bg-gold-600 text-stone-900"
              data-testid="submit-request-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Submit Request
                </>
              )}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
