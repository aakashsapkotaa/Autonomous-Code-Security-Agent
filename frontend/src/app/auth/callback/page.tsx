'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';

export default function AuthCallback() {
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Verifying your email...');

  useEffect(() => {
    const handleEmailConfirmation = async () => {
      try {
        // Get the hash from the URL
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const refreshToken = hashParams.get('refresh_token');
        const type = hashParams.get('type');

        if (type === 'signup' && accessToken) {
          // Set the session
          const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken || '',
          });

          if (error) throw error;

          setStatus('success');
          setMessage('Email verified successfully! Redirecting to dashboard...');
          
          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
        } else if (type === 'recovery') {
          // Handle password recovery
          setStatus('success');
          setMessage('Password reset link verified! Redirecting...');
          setTimeout(() => {
            router.push('/reset-password');
          }, 2000);
        } else {
          // No valid confirmation type found
          setStatus('error');
          setMessage('Invalid confirmation link. Please try signing up again.');
          setTimeout(() => {
            router.push('/');
          }, 3000);
        }
      } catch (error: any) {
        console.error('Email confirmation error:', error);
        setStatus('error');
        setMessage(error.message || 'Failed to verify email. Please try again.');
        setTimeout(() => {
          router.push('/');
        }, 3000);
      }
    };

    handleEmailConfirmation();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center mesh-bg px-6">
      <div className="max-w-md w-full">
        <div className="glass-panel p-8 rounded-2xl border-neon text-center">
          {status === 'loading' && (
            <>
              <div className="w-16 h-16 border-4 border-neon-cyan/30 border-t-neon-cyan rounded-full animate-spin mx-auto mb-6" />
              <h2 className="text-2xl font-headline font-bold text-neon-cyan mb-3">
                Verifying Email
              </h2>
              <p className="text-on-surface-variant">{message}</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-neon-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-headline font-bold text-neon-cyan mb-3">
                Success!
              </h2>
              <p className="text-on-surface-variant">{message}</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 bg-gradient-to-br from-neon-pink/20 to-accent-2/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-neon-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-2xl font-headline font-bold text-neon-pink mb-3">
                Verification Failed
              </h2>
              <p className="text-on-surface-variant">{message}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
