-- ============================================
-- BREEZE SUPABASE RLS POLICIES
-- Run this entire script in Supabase SQL Editor
-- ============================================

-- ============================================
-- 1. HELPER FUNCTIONS
-- ============================================

-- Check if current user is BREEZE admin
CREATE OR REPLACE FUNCTION is_breeze_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM "Roles" 
    WHERE id = auth.uid() 
    AND club_name = 'BREEZE'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get current user's club name
CREATE OR REPLACE FUNCTION get_user_club()
RETURNS TEXT AS $$
BEGIN
  RETURN (
    SELECT club_name FROM "Roles" 
    WHERE id = auth.uid()
    LIMIT 1
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 2. ENABLE RLS ON ALL TABLES
-- ============================================

ALTER TABLE "EventItem" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "MerchItem" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PendingTransaction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "SubmittedTransaction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "ConfirmedEvent" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "ConfirmedMerch" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Roles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "ContactSubmission" ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 3. EventItem POLICIES
-- ============================================

DROP POLICY IF EXISTS "EventItem: Public read" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin insert" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin update" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin delete" ON "EventItem";

CREATE POLICY "EventItem: Public read" ON "EventItem"
  FOR SELECT USING (true);

CREATE POLICY "EventItem: Breeze admin insert" ON "EventItem"
  FOR INSERT WITH CHECK (is_breeze_admin());

CREATE POLICY "EventItem: Breeze admin update" ON "EventItem"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

CREATE POLICY "EventItem: Breeze admin delete" ON "EventItem"
  FOR DELETE USING (is_breeze_admin());

-- ============================================
-- 4. MerchItem POLICIES
-- ============================================

DROP POLICY IF EXISTS "MerchItem: Public read" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin insert" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin update" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin delete" ON "MerchItem";

CREATE POLICY "MerchItem: Public read" ON "MerchItem"
  FOR SELECT USING (true);

CREATE POLICY "MerchItem: Breeze admin insert" ON "MerchItem"
  FOR INSERT WITH CHECK (is_breeze_admin());

CREATE POLICY "MerchItem: Breeze admin update" ON "MerchItem"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

CREATE POLICY "MerchItem: Breeze admin delete" ON "MerchItem"
  FOR DELETE USING (is_breeze_admin());

-- ============================================
-- 5. PendingTransaction POLICIES
-- ============================================

DROP POLICY IF EXISTS "PendingTransaction: Public insert" ON "PendingTransaction";

CREATE POLICY "PendingTransaction: Public insert" ON "PendingTransaction"
  FOR INSERT WITH CHECK (true);

-- No SELECT/UPDATE/DELETE for public - handled server-side only

-- ============================================
-- 6. SubmittedTransaction POLICIES
-- ============================================

DROP POLICY IF EXISTS "SubmittedTransaction: Breeze admin read" ON "SubmittedTransaction";
DROP POLICY IF EXISTS "SubmittedTransaction: Breeze admin update" ON "SubmittedTransaction";

CREATE POLICY "SubmittedTransaction: Breeze admin read" ON "SubmittedTransaction"
  FOR SELECT USING (is_breeze_admin());

CREATE POLICY "SubmittedTransaction: Breeze admin update" ON "SubmittedTransaction"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

-- ============================================
-- 7. ConfirmedEvent POLICIES
-- ============================================

DROP POLICY IF EXISTS "ConfirmedEvent: Breeze admin all" ON "ConfirmedEvent";
DROP POLICY IF EXISTS "ConfirmedEvent: Club admin read own" ON "ConfirmedEvent";

CREATE POLICY "ConfirmedEvent: Breeze admin all" ON "ConfirmedEvent"
  FOR ALL USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

CREATE POLICY "ConfirmedEvent: Club admin read own" ON "ConfirmedEvent"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "EventItem" e
      WHERE e.id = "ConfirmedEvent".id
      AND e.event_org = get_user_club()
    )
  );

-- ============================================
-- 8. ConfirmedMerch POLICIES
-- ============================================

DROP POLICY IF EXISTS "ConfirmedMerch: Breeze admin all" ON "ConfirmedMerch";

CREATE POLICY "ConfirmedMerch: Breeze admin all" ON "ConfirmedMerch"
  FOR ALL USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

-- ============================================
-- 9. Roles POLICIES
-- ============================================

DROP POLICY IF EXISTS "Roles: Read own" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin read all" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin insert" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin update" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin delete" ON "Roles";

CREATE POLICY "Roles: Read own" ON "Roles"
  FOR SELECT USING (id = auth.uid());

CREATE POLICY "Roles: Breeze admin read all" ON "Roles"
  FOR SELECT USING (is_breeze_admin());

CREATE POLICY "Roles: Breeze admin insert" ON "Roles"
  FOR INSERT WITH CHECK (is_breeze_admin());

CREATE POLICY "Roles: Breeze admin update" ON "Roles"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

CREATE POLICY "Roles: Breeze admin delete" ON "Roles"
  FOR DELETE USING (is_breeze_admin());

-- ============================================
-- 10. ContactSubmission POLICIES
-- ============================================

DROP POLICY IF EXISTS "ContactSubmission: Public insert" ON "ContactSubmission";
DROP POLICY IF EXISTS "ContactSubmission: Breeze admin read" ON "ContactSubmission";
DROP POLICY IF EXISTS "ContactSubmission: Breeze admin delete" ON "ContactSubmission";

CREATE POLICY "ContactSubmission: Public insert" ON "ContactSubmission"
  FOR INSERT WITH CHECK (true);

CREATE POLICY "ContactSubmission: Breeze admin read" ON "ContactSubmission"
  FOR SELECT USING (is_breeze_admin());

CREATE POLICY "ContactSubmission: Breeze admin delete" ON "ContactSubmission"
  FOR DELETE USING (is_breeze_admin());

-- ============================================
-- 11. STORAGE BUCKET POLICIES
-- ============================================

-- Assets bucket (event posters, images)
DROP POLICY IF EXISTS "Assets: Public read" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin insert" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin update" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin delete" ON storage.objects;

CREATE POLICY "Assets: Public read" ON storage.objects
  FOR SELECT USING (bucket_id = 'assets');

CREATE POLICY "Assets: Breeze admin insert" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'assets' AND is_breeze_admin());

CREATE POLICY "Assets: Breeze admin update" ON storage.objects
  FOR UPDATE USING (bucket_id = 'assets' AND is_breeze_admin())
  WITH CHECK (bucket_id = 'assets' AND is_breeze_admin());

CREATE POLICY "Assets: Breeze admin delete" ON storage.objects
  FOR DELETE USING (bucket_id = 'assets' AND is_breeze_admin());

-- Transaction-proofs bucket
DROP POLICY IF EXISTS "Transaction-proofs: Public insert" ON storage.objects;
DROP POLICY IF EXISTS "Transaction-proofs: Breeze admin read" ON storage.objects;
DROP POLICY IF EXISTS "Transaction-proofs: Breeze admin delete" ON storage.objects;

CREATE POLICY "Transaction-proofs: Public insert" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'transaction-proofs');

CREATE POLICY "Transaction-proofs: Breeze admin read" ON storage.objects
  FOR SELECT USING (bucket_id = 'transaction-proofs' AND is_breeze_admin());

CREATE POLICY "Transaction-proofs: Breeze admin delete" ON storage.objects
  FOR DELETE USING (bucket_id = 'transaction-proofs' AND is_breeze_admin());

-- ============================================
-- DONE! All RLS policies applied.
-- ============================================
