'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

export default function ConnectionTest() {
  const [status, setStatus] = useState<'testing' | 'success' | 'error'>('testing');
  const [message, setMessage] = useState('Testing connection...');
  const [details, setDetails] = useState<string[]>([]);

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    const testDetails: string[] = [];

    try {
      // Check environment variables
      const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
      const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

      testDetails.push(`URL: ${url ? '✅ Set' : '❌ Missing'}`);
      testDetails.push(`Key: ${key ? '✅ Set' : '❌ Missing'}`);

      if (!url || !key) {
        setStatus('error');
        setMessage('Environment variables not configured');
        setDetails(testDetails);
        return;
      }

      // Test database connection
      testDetails.push('Testing database query...');
      const { data, error } = await supabase
        .from('repositories')
        .select('count')
        .limit(1);

      if (error) {
        testDetails.push(`❌ Query failed: ${error.message}`);
        testDetails.push(`Error code: ${error.code || 'unknown'}`);
        testDetails.push(`Hint: ${error.hint || 'Check your Supabase configuration'}`);
        setStatus('error');
        setMessage('Database connection failed');
        setDetails(testDetails);
        return;
      }

      testDetails.push('✅ Database query successful');
      testDetails.push('✅ Connection established');
      setStatus('success');
      setMessage('Supabase connected successfully!');
      setDetails(testDetails);
    } catch (err) {
      testDetails.push(`❌ Exception: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setStatus('error');
      setMessage('Connection test failed');
      setDetails(testDetails);
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'testing':
        return <div className="w-6 h-6 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />;
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-error" />;
    }
  };

  const getBgColor = () => {
    switch (status) {
      case 'testing':
        return 'bg-primary/10 border-primary/20';
      case 'success':
        return 'bg-green-500/10 border-green-500/20';
      case 'error':
        return 'bg-error/10 border-error/20';
    }
  };

  return (
    <div className={`rounded-xl border p-6 ${getBgColor()}`}>
      <div className="flex items-start gap-4">
        {getIcon()}
        <div className="flex-1">
          <h3 className="text-lg font-headline font-bold text-on-background mb-2">
            {message}
          </h3>
          <div className="space-y-1">
            {details.map((detail, index) => (
              <p key={index} className="text-sm text-on-surface-variant font-mono">
                {detail}
              </p>
            ))}
          </div>
          {status === 'error' && (
            <button
              onClick={testConnection}
              className="mt-4 px-4 py-2 bg-error/20 hover:bg-error/30 text-error rounded-lg transition-colors text-sm font-bold"
            >
              Retry Connection
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
