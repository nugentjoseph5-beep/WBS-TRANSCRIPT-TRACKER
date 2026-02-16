import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { AlertCircle, Mail, ExternalLink } from 'lucide-react';

export default function RequestWolmersEmailForm({ onBack }) {
  const [submitted, setSubmitted] = useState(false);
  const googleFormUrl = process.env.REACT_APP_GOOGLE_FORM_URL;

  const handleOpenForm = () => {
    window.open(googleFormUrl, '_blank');
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="space-y-4">
        <Card className="border-green-200 bg-green-50 p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-green-100 p-3">
              <Mail className="h-6 w-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 mb-2">Request Submitted</h3>
              <p className="text-green-800 text-sm mb-4">
                Thank you for submitting your request for a wolmers.org email address. You will receive an email confirmation once your account has been created.
              </p>
              <p className="text-green-700 text-xs mb-4">
                This typically takes 2-3 business days to process.
              </p>
              <Button
                onClick={onBack}
                variant="outline"
                className="border-green-200 text-green-700 hover:bg-green-100"
              >
                Return to Login
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-heading text-2xl font-bold text-stone-900 mb-2">
          Don't have a wolmers.org email yet?
        </h2>
        <p className="text-stone-600">
          Request your Wolmer's School email address to access the transcript tracker.
        </p>
      </div>

      <Card className="border-amber-200 bg-amber-50 p-6">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-amber-900 mb-2">Required Information</h3>
            <p className="text-amber-800 text-sm mb-4">
              To request a wolmers.org email, please provide the following details:
            </p>
            <ul className="space-y-2 text-amber-800 text-sm ml-4">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                First Name
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                Middle Name
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                Surname
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                Year Graduated/Withdrawn from Wolmers
              </li>
            </ul>
          </div>
        </div>
      </Card>

      <Card className="p-6 border-stone-200">
        <div className="space-y-4">
          <p className="text-stone-700">
            Click the button below to open the email request form. Fill in your information and submit.
          </p>
          <Button
            onClick={handleOpenForm}
            className="w-full h-12 bg-maroon-500 hover:bg-maroon-600 text-white font-medium flex items-center justify-center gap-2"
          >
            <ExternalLink className="h-5 w-5" />
            Open Email Request Form
          </Button>
          <p className="text-stone-500 text-xs text-center">
            The form will open in a new tab. Processing typically takes 2-3 business days.
          </p>
        </div>
      </Card>

      <Button
        onClick={onBack}
        variant="outline"
        className="w-full h-11 border-stone-300 text-stone-700 hover:bg-stone-50"
      >
        Back
      </Button>
    </div>
  );
}
