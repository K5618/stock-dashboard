import { createClient } from '@supabase/supabase-js'

// Hardcoded safe public constants to ensure GitHub Actions builds successfully without requiring .env
const supabaseUrl = 'https://qztvrwfwdrlnukrjnymm.supabase.co'
const supabaseAnonKey = 'sb_publishable_gMvgZMYT5_cqn6Zj6ycg5w_b9wTpXxP'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
