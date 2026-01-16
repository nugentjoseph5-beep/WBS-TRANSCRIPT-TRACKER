import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Eye, EyeOff, Loader2 } from 'lucide-react';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await register({
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
        role: 'student',
      });
      toast.success('Registration successful! Welcome to Wolmer\'s Transcript Tracker.');
      navigate('/student');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Panel - Image */}
      <div 
        className="hidden lg:flex flex-col justify-between p-12 relative"
        style={{
          backgroundImage: `url('https://customer-assets.emergentagent.com/job_wbs-transcripts/artifacts/wneuo6w3_Wolmers-Boys-High-School.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-maroon-500/90 to-maroon-900/95"></div>
        
        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3">
            <img 
              src="https://static.prod-images.emergentagent.com/jobs/13afcd2c-9b31-4868-9eb9-1450f0dbe963/images/7a745def6cecbed258ad447238bdd509434c8ac5c132a51fde220305ad9b582b.png" 
              alt="Wolmer's Boys' School Crest" 
              className="w-14 h-14 object-contain"
            />
            <div>
              <h1 className="font-heading text-white text-xl font-semibold">Wolmer's Boys' School</h1>
              <p className="text-gold-400 text-sm">Est. 1729</p>
            </div>
          </Link>
        </div>

        <div className="relative z-10 space-y-6">
          <h2 className="font-heading text-3xl text-white font-bold">
            Join Our Transcript System
          </h2>
          <ul className="space-y-3 text-white/80">
            <li className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-gold-500 text-maroon-900 flex items-center justify-center text-sm font-bold">✓</span>
              Request transcripts online
            </li>
            <li className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-gold-500 text-maroon-900 flex items-center justify-center text-sm font-bold">✓</span>
              Track your request status
            </li>
            <li className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-gold-500 text-maroon-900 flex items-center justify-center text-sm font-bold">✓</span>
              Get notified of updates
            </li>
          </ul>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-3">
              <img 
                src="https://static.prod-images.emergentagent.com/jobs/13afcd2c-9b31-4868-9eb9-1450f0dbe963/images/7a745def6cecbed258ad447238bdd509434c8ac5c132a51fde220305ad9b582b.png" 
                alt="Wolmer's Boys' School Crest" 
                className="w-12 h-12 object-contain"
              />
              <div className="text-left">
                <h1 className="font-heading text-stone-900 text-lg font-semibold">Wolmer's Boys' School</h1>
                <p className="text-stone-500 text-sm">Transcript Tracker</p>
              </div>
            </Link>
          </div>

          <div>
            <h2 className="font-heading text-3xl font-bold text-stone-900 mb-2">Create your account</h2>
            <p className="text-stone-600">Register as a student to request transcripts</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" data-testid="register-form">
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                name="full_name"
                type="text"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={handleChange}
                required
                className="h-12 focus:ring-maroon-500"
                data-testid="register-name-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email address</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
                required
                className="h-12 focus:ring-maroon-500"
                data-testid="register-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a password (min 6 characters)"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength={6}
                  className="h-12 pr-12 focus:ring-maroon-500"
                  data-testid="register-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-500 hover:text-stone-700"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="h-12 focus:ring-maroon-500"
                data-testid="register-confirm-password-input"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-maroon-500 hover:bg-maroon-600 text-white font-medium"
              data-testid="register-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          <div className="text-center">
            <p className="text-stone-600">
              Already have an account?{' '}
              <Link to="/login" className="text-maroon-500 hover:text-maroon-600 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
