import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_https://ayeoqnvldhrazjpvbrey.supabase.co;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Supabase environment variables missing!');
  console.error('Please check your .env.local file');
  throw new Error('Missing Supabase environment variables. Check .env.local file.');
}

// Validate the anon key format (should be a JWT with 3 parts)
const keyParts = supabaseAnonKey.split('.');
if (keyParts.length !== 3) {
  console.error('❌ Invalid Supabase anon key format!');
  console.error('The key should be a JWT token with 3 parts separated by dots');
  console.error('Get the correct key from: Supabase Dashboard → Settings → API');
  throw new Error('Invalid Supabase anon key format. Please check your .env.local file.');
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
