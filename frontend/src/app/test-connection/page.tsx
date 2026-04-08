'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabaseClient';
import ConnectionTest from '@/components/ConnectionTest';

export default function TestConnectionPage() {
  const [manualTest, setManualTest] = useState<{
    status: 'idle' | 'testing' | 'success' | 'error';
    message: string;
    data?: any;
  }>({ status: 'idle', message: '' });

  const runManualTest = async () => {
    setManualTest({ status: 'testing', message: 'Testing...' });

    try {
      const { data, error } = await supabase
        .from('repositories')
        .select('*')
        .limit(5);

      if (error) {
        setManualTest({
          status: 'error',
          message: `Error: ${error.message}`,
          data: error,
        });
        return;
      }

      setManualTest({
        status: 'success',
        message: `Success! Found ${data?.length || 0} repositories`,
        data,
      });
    } catch (err) {
      setManualTest({
        status: 'error',
        message: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-headline font-bold text-on-background mb-2">
            Supabase Connection Test
          </h1>
          <p className="text-on-surface-variant">
            Verify your Supabase configuration is working correctly
          </p>
        </div>

        <ConnectionTest />

        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <h2 className="text-xl font-headline font-bold text-on-background mb-4">
            Manual Test
          </h2>
          <button
            onClick={runManualTest}
            disabled={manualTest.status === 'testing'}
            className="px-6 py-3 bg-primary hover:bg-primary-container text-on-primary-container font-bold rounded-lg transition-colors disabled:opacity-50"
          >
            {manualTest.status === 'testing' ? 'Testing...' : 'Run Manual Test'}
          </button>

          {manualTest.status !== 'idle' && (
            <div className="mt-4 p-4 bg-surface-container-low rounded-lg">
              <p className="text-sm font-bold text-on-background mb-2">
                Status: {manualTest.status}
              </p>
              <p className="text-sm text-on-surface-variant mb-2">
                {manualTest.message}
              </p>
              {manualTest.data && (
                <pre className="text-xs text-on-surface-variant overflow-auto p-4 bg-surface-container rounded">
                  {JSON.stringify(manualTest.data, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>

        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <h2 className="text-xl font-headline font-bold text-on-background mb-4">
            Environment Variables
          </h2>
          <div className="space-y-2 text-sm font-mono">
            <div>
              <span className="text-on-surface-variant">NEXT_PUBLIC_https://ayeoqnvldhrazjpvbrey.supabase.co:</span>{' '}
              <span className="text-on-background">
                {process.env.NEXT_PUBLIC_https://ayeoqnvldhrazjpvbrey.supabase.co || '❌ Not set'}
              </span>
            </div>
            <div>
              <span className="text-on-surface-variant">NEXT_PUBLIC_SUPABASE_ANON_KEY:</span>{' '}
              <span className="text-on-background">
                {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
                  ? `✅ Set (${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY.substring(0, 20)}...)`
                  : '❌ Not set'}
              </span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <h2 className="text-xl font-headline font-bold text-on-background mb-4">
            Quick Setup Steps
          </h2>
          <ol className="list-decimal list-inside space-y-2 text-on-surface-variant">
            <li>Go to your Supabase project dashboard</li>
            <li>Click Settings → API</li>
            <li>Copy the Project URL and anon/public key</li>
            <li>Update .env.local with these values</li>
            <li>Run the schema.sql in SQL Editor</li>
            <li>Run the supabase-rls-policies.sql to configure access</li>
            <li>Restart the dev server</li>
          </ol>
          <a
            href="/SETUP_GUIDE.md"
            className="inline-block mt-4 text-primary hover:text-primary-container"
          >
            View detailed setup guide →
          </a>
        </div>
      </div>
    </div>
  );
}
