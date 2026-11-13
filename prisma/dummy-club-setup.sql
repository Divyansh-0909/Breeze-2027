-- ============================================
-- Breeze 2027 - Dummy Club Setup SQL
-- ============================================
-- 
-- This script creates a test club account with:
-- - A Supabase auth user
-- - A Roles entry linking the user to "TEST CLUB"
-- - Sample events for the club
-- - Sample approved transactions
--
-- CREDENTIALS:
--   Email: testclub@breeze2027.com
--   Password: TestClub@2027
--   Dashboard URL: http://localhost:3000/admin/clubs
--
-- ============================================

-- STEP 1: Create the auth user via Supabase Dashboard or CLI
-- Go to: Supabase Dashboard -> Authentication -> Users -> Invite User
-- Email: testclub@breeze2027.com  
-- Password: TestClub@2027
-- 
-- After creating the user, note the UUID and replace below:
-- (You can also use the Supabase SQL Editor to create the user)

-- If using Supabase SQL Editor with service role:
-- Note: Direct auth.users INSERT requires service_role access
-- It's recommended to use the Supabase Dashboard to create the user

-- STEP 2: Create the role entry (run AFTER creating the auth user)
-- Replace 'YOUR_USER_UUID' with the actual UUID from the auth user
-- INSERT INTO "Roles" (id, club_name, email) 
-- VALUES ('YOUR_USER_UUID', 'TEST CLUB', 'testclub@breeze2027.com');

-- STEP 3: Create sample events for the test club
INSERT INTO "EventItem" (event_name, event_description, event_price, event_type, event_venue, event_date, event_org, image_url, registration_open)
VALUES 
  ('Rhythm & Blues Night', 'An evening of soulful music performances featuring talented artists from across the campus.', 150, 'Cultural', 'Open Air Theatre', 'Feb 15th 2027', 'TEST CLUB', 'https://via.placeholder.com/400x300?text=Rhythm+Blues', true),
  ('Code Sprint 2027', 'A 6-hour competitive coding challenge for beginners and intermediates. Solo or pair entries allowed.', 200, 'Technical', 'Computer Lab A', 'Feb 16th 2027', 'TEST CLUB', 'https://via.placeholder.com/400x300?text=Code+Sprint', true),
  ('Art Exhibition', 'Showcasing student artwork including paintings, digital art, and sculptures. Open to all visitors.', 50, 'Cultural', 'Gallery Hall', 'Feb 17th 2027', 'TEST CLUB', 'https://via.placeholder.com/400x300?text=Art+Exhibition', false);

-- STEP 4: Create sample approved transactions for the test club events
-- First get the event IDs from the inserts above. We'll use a CTE approach:

-- Create a test approved transaction
INSERT INTO "SubmittedTransaction" (token, name, email, phone, address, amount, cart, approved, rejected, email_sent, accommodation, accommodation_price, student_details)
VALUES 
  ('TEST_TX_001', 'Rahul Sharma', 'rahul@test.com', '9876543210', 'R2024001', 350, '{}', true, false, true, '{}', 0, 'B.Tech CSE - 2nd Year'),
  ('TEST_TX_002', 'Priya Patel', 'priya@test.com', '9876543211', 'R2024002', 200, '{}', true, false, true, '{}', 0, 'B.Tech ECE - 3rd Year'),
  ('TEST_TX_003', 'Amit Kumar', 'amit@test.com', '9876543212', 'R2024003', 150, '{}', true, false, true, '{}', 0, 'B.Tech IT - 1st Year');

-- Link transactions to events (ConfirmedEvent entries)
-- Note: You need to replace the event IDs with actual UUIDs from your database
-- Run this after the event inserts to get the IDs:
-- SELECT id, event_name FROM "EventItem" WHERE event_org = 'TEST CLUB';

-- Then insert confirmed events like:
-- INSERT INTO "ConfirmedEvent" (token, id, quantity) VALUES
--   ('TEST_TX_001', '<rhythm_blues_id>', 1),
--   ('TEST_TX_001', '<code_sprint_id>', 1),
--   ('TEST_TX_002', '<code_sprint_id>', 1),
--   ('TEST_TX_003', '<rhythm_blues_id>', 1);

-- ============================================
-- AUTOMATED VERSION (run all at once)
-- ============================================
-- This version uses CTEs to automatically link events to transactions

DO $$
DECLARE
  ev1_id UUID;
  ev2_id UUID;
  ev3_id UUID;
BEGIN
  -- Get the IDs of the test club events we just inserted
  SELECT id INTO ev1_id FROM "EventItem" WHERE event_name = 'Rhythm & Blues Night' AND event_org = 'TEST CLUB' LIMIT 1;
  SELECT id INTO ev2_id FROM "EventItem" WHERE event_name = 'Code Sprint 2027' AND event_org = 'TEST CLUB' LIMIT 1;
  SELECT id INTO ev3_id FROM "EventItem" WHERE event_name = 'Art Exhibition' AND event_org = 'TEST CLUB' LIMIT 1;

  -- Link transactions to events
  IF ev1_id IS NOT NULL AND ev2_id IS NOT NULL THEN
    INSERT INTO "ConfirmedEvent" (token, id, quantity) VALUES
      ('TEST_TX_001', ev1_id, 1),
      ('TEST_TX_001', ev2_id, 1),
      ('TEST_TX_002', ev2_id, 1),
      ('TEST_TX_003', ev1_id, 1)
    ON CONFLICT DO NOTHING;
  END IF;
END $$;
