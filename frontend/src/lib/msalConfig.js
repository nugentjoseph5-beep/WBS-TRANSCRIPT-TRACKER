import { PublicClientApplication, LogLevel } from '@azure/msal-browser';

const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_MICROSOFT_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${process.env.REACT_APP_MICROSOFT_TENANT_ID}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        if (level === LogLevel.Error) console.error(message);
      },
    },
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

// Scopes for Microsoft Graph API
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

// Validate if email is a wolmers.org email
export const isWolmersEmail = (email) => {
  return email && email.toLowerCase().endsWith('@wolmers.org');
};

// Extract name and graduation year from email
// Format: firstname.lastname.graduationyear@wolmers.org
export const parseWolmersEmail = (email) => {
  const localPart = email.split('@')[0];
  const parts = localPart.split('.');
  
  if (parts.length >= 3) {
    const graduationYear = parts[parts.length - 1];
    const lastName = parts[parts.length - 2];
    const firstName = parts.slice(0, -2).join(' ');
    
    return {
      firstName,
      lastName,
      graduationYear: isNaN(graduationYear) ? null : graduationYear,
    };
  }
  
  return null;
};
