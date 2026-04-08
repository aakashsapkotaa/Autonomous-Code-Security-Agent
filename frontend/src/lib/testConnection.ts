/**
 * Test script to verify Supabase connection
 * Run this to ensure your database is properly configured
 */

import { supabase } from './supabaseClient';

export async function testSupabaseConnection() {
  console.log('🔍 Testing Supabase connection...');
  
  try {
    // Test 1: Check if client is initialized
    if (!supabase) {
      throw new Error('Supabase client not initialized');
    }
    console.log('✅ Supabase client initialized');

    // Test 2: Try to fetch from repositories table
    const { data, error } = await supabase
      .from('repositories')
      .select('count')
      .limit(1);

    if (error) {
      console.error('❌ Database query failed:', error.message);
      return false;
    }

    console.log('✅ Successfully connected to database');
    console.log('✅ Repositories table accessible');
    
    return true;
  } catch (err) {
    console.error('❌ Connection test failed:', err);
    return false;
  }
}

// Uncomment to run test directly
// testSupabaseConnection();
