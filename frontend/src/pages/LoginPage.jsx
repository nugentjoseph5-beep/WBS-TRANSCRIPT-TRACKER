import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Eye, EyeOff, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.full_name}!`);
      
      // Redirect based on role
      if (user.role === 'student') navigate('/student');
      else if (user.role === 'staff') navigate('/staff');
      else if (user.role === 'admin') navigate('/admin');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid email or password');
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
          backgroundImage: `url('https://images.unsplash.com/photo-1705756566946-f39616809f5c?crop=entropy&cs=srgb&fm=jpg&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-maroon-500/90 to-maroon-900/95"></div>
        
        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gold-500 flex items-center justify-center">
              <span className="font-heading text-maroon-500 text-xl font-bold">W</span>
            </div>
            <div>
              <h1 className="font-heading text-white text-xl font-semibold">Wolmer's Boys' School</h1>
              <p className="text-gold-400 text-sm">Est. 1729</p>
            </div>
          </Link>
        </div>

        <div className="relative z-10">
          <blockquote className="text-xl text-white/90 font-light leading-relaxed mb-4">
            "Age Quod Agis - Do well whatever you do"
          </blockquote>
          <p className="text-gold-400 text-sm">School Motto</p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-maroon-500 flex items-center justify-center">
                <span className="font-heading text-gold-500 text-xl font-bold">W</span>
              </div>
              <div className="text-left">
                <h1 className="font-heading text-stone-900 text-lg font-semibold">Wolmer's Boys' School</h1>
                <p className="text-stone-500 text-sm">Transcript Tracker</p>
              </div>
            </Link>
          </div>

          <div>
            <h2 className="font-heading text-3xl font-bold text-stone-900 mb-2">Welcome back</h2>
            <p className="text-stone-600">Sign in to access your transcript requests</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6" data-testid="login-form">
            <div className="space-y-2">
              <Label htmlFor="email">Email address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 focus:ring-maroon-500"
                data-testid="login-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-12 pr-12 focus:ring-maroon-500"
                  data-testid="login-password-input"
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

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-maroon-500 hover:bg-maroon-600 text-white font-medium"
              data-testid="login-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="text-center">
            <p className="text-stone-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-maroon-500 hover:text-maroon-600 font-medium">
                Register as a student
              </Link>
            </p>
          </div>

          {/* Quick access hint */}
          <div className="pt-6 border-t border-stone-200">
            <p className="text-stone-500 text-sm text-center">
              Staff and admin accounts are created by administrators.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
