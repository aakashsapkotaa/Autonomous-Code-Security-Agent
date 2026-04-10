import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Supabase environment variables missing!');
  console.error('');
  console.error('📋 Troubleshooting Steps:');
  console.error('1. Check that .env.local exists in the frontend directory');
  console.error('2. Verify these variables are set:');
  console.error('   - NEXT_PUBLIC_SUPABASE_URL');
  console.error('   - NEXT_PUBLIC_SUPABASE_ANON_KEY');
  console.error('3. Get your credentials from: Supabase Dashboard → Settings → API');
  console.error('4. Restart your development server after updating .env.local');
  console.error('');
  console.error('📖 Configuration Guide: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs');
  throw new Error('Missing Supabase environment variables. Follow the troubleshooting steps above.');
}

// Validate the anon key format (should be a JWT with 3 parts)
const keyParts = supabaseAnonKey.split('.');
if (keyParts.length !== 3) {
  console.error('❌ Invalid Supabase anon key format!');
  console.error('');
  console.error('📋 Step-by-step fix:');
  console.error('1. Go to: Supabase Dashboard → Your Project → Settings → API');
  console.error('2. Copy the "anon public" key (not the service_role key)');
  console.error('3. The key should look like: eyJhbG...long string...xyz');
  console.error('4. Update NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local');
  console.error('5. Restart your development server');
  console.error('');
  console.error('⚠️  Common mistakes:');
  console.error('   - Using service_role key instead of anon key');
  console.error('   - Extra spaces or quotes around the key');
  console.error('   - Incomplete key (should be 3 parts separated by dots)');
  throw new Error('Invalid Supabase anon key format. Follow the step-by-step fix above.');
}

console.log('✅ Supabase client initializing...');
console.log('   URL:', supabaseUrl);
console.log('   Key:', supabaseAnonKey.substring(0, 30) + '...');

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
