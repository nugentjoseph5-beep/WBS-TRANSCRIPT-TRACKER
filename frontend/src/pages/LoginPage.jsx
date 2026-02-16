import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { useMsal } from '@azure/msal-react';
import { loginRequest, isWolmersEmail } from '@/lib/msalConfig';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Eye, EyeOff, Loader2, Mail } from 'lucide-react';
import RequestWolmersEmailForm from '@/components/RequestWolmersEmailForm';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showEmailRequest, setShowEmailRequest] = useState(false);
  const [loginMode, setLoginMode] = useState('microsoft'); // 'microsoft' or 'traditional'
  const { login, loginWithMicrosoft } = useAuth();
  const navigate = useNavigate();
  const { instance } = useMsal();

  const handleMicrosoftLogin = async () => {
    setLoading(true);
    try {
      const response = await instance.loginPopup(loginRequest);
      const email = response.account.username;

      if (!isWolmersEmail(email)) {
        toast.error('Please use your wolmers.org email address');
        await instance.logoutPopup({ account: response.account });
        setShowEmailRequest(true);
        setLoading(false);
        return;
      }

      const user = await loginWithMicrosoft({
        email,
        name: response.account.name,
        microsoftToken: response.accessToken,
      });

      toast.success(`Welcome back, ${user.full_name}!`);

      if (user.role === 'student') navigate('/student');
      else if (user.role === 'staff') navigate('/staff');
      else if (user.role === 'admin') navigate('/admin');
    } catch (error) {
      if (error.errorCode === 'user_cancelled') {
        // User cancelled login, don't show error
      } else {
        toast.error(error.errorCode === 'user_cancelled' ? 'Login cancelled' : 'Microsoft login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTraditionalLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.full_name}!`);

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
          backgroundImage: `url('https://customer-assets.emergentagent.com/job_wbs-transcripts/artifacts/wneuo6w3_Wolmers-Boys-High-School.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-maroon-500/90 to-maroon-900/95"></div>
        
        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3">
            <img 
              src="https://customer-assets.emergentagent.com/job_13afcd2c-9b31-4868-9eb9-1450f0dbe963/artifacts/iuukr0xo_Wolmer%27s_Schools.png" 
              alt="Wolmer's Boys' School Crest" 
              className="w-14 h-14 object-contain"
            />
            <div>
              <h1 className="font-heading text-white text-xl font-semibold">Wolmer's Boys' School</h1>
              <p className="text-gold-400 text-sm">Est. 1729</p>
            </div>
          </Link>
        </div>

        <div className="relative z-10">
          <blockquote className="text-xl text-white/90 font-light leading-relaxed mb-4">
            "Age Quod Agis: Whatever you do, do it to the best of your ability"
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
              <img 
                src="https://customer-assets.emergentagent.com/job_13afcd2c-9b31-4868-9eb9-1450f0dbe963/artifacts/iuukr0xo_Wolmer%27s_Schools.png" 
                alt="Wolmer's Boys' School Crest" 
                className="w-12 h-12 object-contain"
              />
              <div className="text-left">
                <h1 className="font-heading text-stone-900 text-lg font-semibold">Wolmer's Boys' School</h1>
                <p className="text-stone-500 text-sm">Transcript Tracker</p>
              </div>
            </Link>
          </div>

          {/* Email Request Form */}
          {showEmailRequest ? (
            <RequestWolmersEmailForm onBack={() => setShowEmailRequest(false)} />
          ) : (
            <>
              <div>
                <h2 className="font-heading text-3xl font-bold text-stone-900 mb-2">Welcome back</h2>
                <p className="text-stone-600">Sign in to access your transcript requests</p>
              </div>

              {/* Microsoft 365 Sign In */}
              {loginMode === 'microsoft' && (
                <div className="space-y-4">
                  <Button
                    onClick={handleMicrosoftLogin}
                    disabled={loading}
                    className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-medium flex items-center justify-center gap-3"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      <>
                        <Mail className="h-5 w-5" />
                        Sign in with Microsoft 365
                      </>
                    )}
                  </Button>

                  <p className="text-center text-sm text-stone-600">
                    Use your <span className="font-medium text-stone-900">wolmers.org</span> email address
                  </p>

                  <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-stone-200"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-2 bg-white text-stone-500">or</span>
                    </div>
                  </div>

                  <Button
                    onClick={() => setLoginMode('traditional')}
                    variant="outline"
                    className="w-full h-11 border-stone-300 text-stone-700 hover:bg-stone-50"
                  >
                    Sign in with Password
                  </Button>

                  <Button
                    onClick={() => setShowEmailRequest(true)}
                    variant="ghost"
                    className="w-full h-11 text-maroon-500 hover:bg-maroon-50"
                  >
                    Don't have a wolmers.org email? Request one
                  </Button>
                </div>
              )}

              {/* Traditional Login */}
              {loginMode === 'traditional' && (
                <>
                  <form onSubmit={handleTraditionalLogin} className="space-y-6">
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
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="password">Password</Label>
                        <Link to="/forgot-password" className="text-sm text-maroon-500 hover:text-maroon-600">
                          Forgot password?
                        </Link>
                      </div>
                      <div className="relative">
                        <Input
                          id="password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="Enter your password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          required
                          className="h-12 pr-12 focus:ring-maroon-500"
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

                  <Button
                    onClick={() => setLoginMode('microsoft')}
                    variant="outline"
                    className="w-full h-11 border-stone-300 text-stone-700 hover:bg-stone-50"
                  >
                    Back to Microsoft 365 Sign In
                  </Button>
                </>
              )}

              <div className="text-center">
                <p className="text-stone-600">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-maroon-500 hover:text-maroon-600 font-medium">
                    Create one here
                  </Link>
                </p>
              </div>

              {/* Quick access hint */}
              <div className="pt-6 border-t border-stone-200">
                <p className="text-stone-500 text-sm text-center">
                  Staff and admin accounts are created by administrators.
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
