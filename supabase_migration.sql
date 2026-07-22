-- ============================================
-- BREEZE 2027 SUPABASE MIGRATION SCRIPT
-- Idempotent script to setup the full database
-- ============================================

-- ============================================
-- 1. ENUMS
-- ============================================

DO $$ BEGIN
    CREATE TYPE event_category AS ENUM ('Cultural', 'Technical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE accommodation_option AS ENUM ('DAY1', 'DAY2', 'DAY3');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- 2. TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS "EventItem" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "event_name" TEXT NOT NULL DEFAULT '',
    "event_description" TEXT NOT NULL DEFAULT '',
    "event_price" SMALLINT NOT NULL,
    "event_org" TEXT,
    "event_venue" TEXT,
    "event_date" TEXT,
    "image_url" TEXT,
    "event_type" event_category,
    "registration_open" BOOLEAN NOT NULL DEFAULT true,
    "event_end_date" TEXT,
    "event_pair_price" SMALLINT,
    CONSTRAINT "EventItem_pkey" PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "MerchItem" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "product_name" TEXT NOT NULL,
    "product_price" SMALLINT NOT NULL DEFAULT 0,
    "product_description" TEXT NOT NULL DEFAULT '',
    "image_url" TEXT,
    CONSTRAINT "MerchItem_pkey" PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "PendingTransaction" (
    "id" TEXT NOT NULL,
    "amount" BIGINT NOT NULL,
    "time" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "cart" JSONB NOT NULL,
    "accommodation" accommodation_option[],
    "accommodation_price" BIGINT NOT NULL,
    CONSTRAINT "PendingTransaction_pkey" PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "SubmittedTransaction" (
    "token" VARCHAR NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "name" TEXT NOT NULL DEFAULT '',
    "email" TEXT NOT NULL DEFAULT '',
    "phone" TEXT NOT NULL DEFAULT '',
    "address" TEXT NOT NULL DEFAULT '',
    "amount" BIGINT NOT NULL DEFAULT 0,
    "proof" TEXT DEFAULT '',
    "cart" JSONB NOT NULL,
    "approved" BOOLEAN DEFAULT false,
    "rejected" BOOLEAN NOT NULL DEFAULT false,
    "rejection_reason" TEXT,
    "email_sent" BOOLEAN NOT NULL DEFAULT false,
    "accommodation" accommodation_option[],
    "accommodation_price" BIGINT NOT NULL,
    "student_details" TEXT,
    CONSTRAINT "SubmittedTransaction_pkey" PRIMARY KEY ("token")
);

CREATE TABLE IF NOT EXISTS "ConfirmedEvent" (
    "token" VARCHAR NOT NULL,
    "id" UUID NOT NULL,
    "quantity" BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT "confirmedEvent_pkey" PRIMARY KEY ("token", "id")
);

CREATE TABLE IF NOT EXISTS "ConfirmedMerch" (
    "token" VARCHAR NOT NULL,
    "id" UUID NOT NULL,
    "size" TEXT NOT NULL DEFAULT '',
    "quantity" BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT "ConfirmedMerch_pkey" PRIMARY KEY ("token", "id", "size")
);

CREATE TABLE IF NOT EXISTS "Roles" (
    "id" UUID NOT NULL,
    "club_name" TEXT NOT NULL DEFAULT '',
    "email" TEXT NOT NULL DEFAULT '',
    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ContactSubmission" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    CONSTRAINT "ContactSubmission_pkey" PRIMARY KEY ("id")
);

-- ============================================
-- 3. FOREIGN KEYS
-- ============================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'confirmedEvent_id_fkey') THEN
        ALTER TABLE "ConfirmedEvent" ADD CONSTRAINT "confirmedEvent_id_fkey" 
        FOREIGN KEY ("id") REFERENCES "EventItem"("id") ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'confirmedEvent_token_fkey') THEN
        ALTER TABLE "ConfirmedEvent" ADD CONSTRAINT "confirmedEvent_token_fkey" 
        FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'confirmedMerch_id_fkey') THEN
        ALTER TABLE "ConfirmedMerch" ADD CONSTRAINT "confirmedMerch_id_fkey" 
        FOREIGN KEY ("id") REFERENCES "MerchItem"("id") ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'confirmedMerch_token_fkey') THEN
        ALTER TABLE "ConfirmedMerch" ADD CONSTRAINT "confirmedMerch_token_fkey" 
        FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================
-- 4. HELPER FUNCTIONS
-- ============================================

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
-- 5. ENABLE RLS ON ALL TABLES
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
-- 6. RLS POLICIES
-- ============================================

-- EventItem
DROP POLICY IF EXISTS "EventItem: Public read" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin insert" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin update" ON "EventItem";
DROP POLICY IF EXISTS "EventItem: Breeze admin delete" ON "EventItem";

CREATE POLICY "EventItem: Public read" ON "EventItem" FOR SELECT USING (true);
CREATE POLICY "EventItem: Breeze admin insert" ON "EventItem" FOR INSERT WITH CHECK (is_breeze_admin());
CREATE POLICY "EventItem: Breeze admin update" ON "EventItem" FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "EventItem: Breeze admin delete" ON "EventItem" FOR DELETE USING (is_breeze_admin());

-- MerchItem
DROP POLICY IF EXISTS "MerchItem: Public read" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin insert" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin update" ON "MerchItem";
DROP POLICY IF EXISTS "MerchItem: Breeze admin delete" ON "MerchItem";

CREATE POLICY "MerchItem: Public read" ON "MerchItem" FOR SELECT USING (true);
CREATE POLICY "MerchItem: Breeze admin insert" ON "MerchItem" FOR INSERT WITH CHECK (is_breeze_admin());
CREATE POLICY "MerchItem: Breeze admin update" ON "MerchItem" FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "MerchItem: Breeze admin delete" ON "MerchItem" FOR DELETE USING (is_breeze_admin());

-- PendingTransaction
DROP POLICY IF EXISTS "PendingTransaction: Public insert" ON "PendingTransaction";
CREATE POLICY "PendingTransaction: Public insert" ON "PendingTransaction" FOR INSERT WITH CHECK (true);

-- SubmittedTransaction
DROP POLICY IF EXISTS "SubmittedTransaction: Breeze admin read" ON "SubmittedTransaction";
DROP POLICY IF EXISTS "SubmittedTransaction: Breeze admin update" ON "SubmittedTransaction";
CREATE POLICY "SubmittedTransaction: Breeze admin read" ON "SubmittedTransaction" FOR SELECT USING (is_breeze_admin());
CREATE POLICY "SubmittedTransaction: Breeze admin update" ON "SubmittedTransaction" FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

-- ConfirmedEvent
DROP POLICY IF EXISTS "ConfirmedEvent: Breeze admin all" ON "ConfirmedEvent";
DROP POLICY IF EXISTS "ConfirmedEvent: Club admin read own" ON "ConfirmedEvent";
CREATE POLICY "ConfirmedEvent: Breeze admin all" ON "ConfirmedEvent" FOR ALL USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "ConfirmedEvent: Club admin read own" ON "ConfirmedEvent" FOR SELECT USING (
    EXISTS (SELECT 1 FROM "EventItem" e WHERE e.id = "ConfirmedEvent".id AND e.event_org = get_user_club())
);

-- ConfirmedMerch
DROP POLICY IF EXISTS "ConfirmedMerch: Breeze admin all" ON "ConfirmedMerch";
CREATE POLICY "ConfirmedMerch: Breeze admin all" ON "ConfirmedMerch" FOR ALL USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());

-- Roles
DROP POLICY IF EXISTS "Roles: Read own" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin read all" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin insert" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin update" ON "Roles";
DROP POLICY IF EXISTS "Roles: Breeze admin delete" ON "Roles";
CREATE POLICY "Roles: Read own" ON "Roles" FOR SELECT USING (id = auth.uid());
CREATE POLICY "Roles: Breeze admin read all" ON "Roles" FOR SELECT USING (is_breeze_admin());
CREATE POLICY "Roles: Breeze admin insert" ON "Roles" FOR INSERT WITH CHECK (is_breeze_admin());
CREATE POLICY "Roles: Breeze admin update" ON "Roles" FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "Roles: Breeze admin delete" ON "Roles" FOR DELETE USING (is_breeze_admin());

-- ContactSubmission
DROP POLICY IF EXISTS "ContactSubmission: Public insert" ON "ContactSubmission";
DROP POLICY IF EXISTS "ContactSubmission: Breeze admin read" ON "ContactSubmission";
DROP POLICY IF EXISTS "ContactSubmission: Breeze admin delete" ON "ContactSubmission";
CREATE POLICY "ContactSubmission: Public insert" ON "ContactSubmission" FOR INSERT WITH CHECK (true);
CREATE POLICY "ContactSubmission: Breeze admin read" ON "ContactSubmission" FOR SELECT USING (is_breeze_admin());
CREATE POLICY "ContactSubmission: Breeze admin delete" ON "ContactSubmission" FOR DELETE USING (is_breeze_admin());


-- ============================================
-- 7. STORAGE BUCKETS & POLICIES
-- ============================================

-- Create buckets if they don't exist
INSERT INTO storage.buckets (id, name, public) VALUES ('assets', 'assets', true) ON CONFLICT (id) DO UPDATE SET public = true;
INSERT INTO storage.buckets (id, name, public) VALUES ('transaction-proofs', 'transaction-proofs', false) ON CONFLICT (id) DO UPDATE SET public = false;

-- Assets bucket policies
DROP POLICY IF EXISTS "Assets: Public read" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin insert" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin update" ON storage.objects;
DROP POLICY IF EXISTS "Assets: Breeze admin delete" ON storage.objects;

CREATE POLICY "Assets: Public read" ON storage.objects FOR SELECT USING (bucket_id = 'assets');
CREATE POLICY "Assets: Breeze admin insert" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'assets' AND is_breeze_admin());
CREATE POLICY "Assets: Breeze admin update" ON storage.objects FOR UPDATE USING (bucket_id = 'assets' AND is_breeze_admin()) WITH CHECK (bucket_id = 'assets' AND is_breeze_admin());
CREATE POLICY "Assets: Breeze admin delete" ON storage.objects FOR DELETE USING (bucket_id = 'assets' AND is_breeze_admin());

-- Transaction-proofs bucket policies
DROP POLICY IF EXISTS "Transaction-proofs: Public insert" ON storage.objects;
DROP POLICY IF EXISTS "Transaction-proofs: Breeze admin read" ON storage.objects;
DROP POLICY IF EXISTS "Transaction-proofs: Breeze admin delete" ON storage.objects;

CREATE POLICY "Transaction-proofs: Public insert" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'transaction-proofs');
CREATE POLICY "Transaction-proofs: Breeze admin read" ON storage.objects FOR SELECT USING (bucket_id = 'transaction-proofs' AND is_breeze_admin());
CREATE POLICY "Transaction-proofs: Breeze admin delete" ON storage.objects FOR DELETE USING (bucket_id = 'transaction-proofs' AND is_breeze_admin());

-- TRIGGERS
-- No explicit Postgres triggers found or implied in code. 
-- User creation in the 'Roles' table is handled by the application code during signup (server action).

-- ============================================
-- DONE
-- ============================================
