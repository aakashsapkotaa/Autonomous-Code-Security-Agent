import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

if (!PUBLIC_SUPABASE_URL || !PUBLIC_SUPABASE_ANON_KEY) {
  console.error('❌ Supabase environment variables missing!');
  throw new Error('Missing Supabase environment variables');
}

const keyParts = PUBLIC_SUPABASE_ANON_KEY.split('.');
if (keyParts.length !== 3) {
  console.error('❌ Invalid Supabase anon key format!');
  throw new Error('Invalid Supabase anon key format');
}

console.log('✅ Supabase client initializing...');
console.log('   URL:', PUBLIC_SUPABASE_URL);
console.log('   Key:', PUBLIC_SUPABASE_ANON_KEY.substring(0, 30) + '...');

export const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
