-- ============================================
-- BREEZE LIVE TIMELINE — SUPABASE SETUP (draft, disabled by default)
-- Idempotent. Run in the Supabase SQL Editor AFTER the main
-- supabase_migration.sql. The frontend only reads these tables when
-- NEXT_PUBLIC_TIMELINE_SOURCE=supabase; otherwise it serves mock data.
-- Requires the is_breeze_admin() helper from the main migration.
-- ============================================

-- 1. TABLES
CREATE TABLE IF NOT EXISTS "TimelineEvent" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "title" TEXT NOT NULL DEFAULT '',
    "artist" TEXT NOT NULL DEFAULT '',
    "stage" TEXT NOT NULL DEFAULT 'Main Stage',
    "description" TEXT NOT NULL DEFAULT '',
    "start_time" TIMESTAMPTZ(6) NOT NULL,
    "end_time" TIMESTAMPTZ(6) NOT NULL,
    "status" TEXT,
    "poster_url" TEXT,
    "featured" BOOLEAN NOT NULL DEFAULT false,
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    CONSTRAINT "TimelineEvent_pkey" PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "TimelineAnnouncement" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "message" TEXT NOT NULL,
    "severity" TEXT NOT NULL DEFAULT 'info',
    "active" BOOLEAN NOT NULL DEFAULT true,
    CONSTRAINT "TimelineAnnouncement_pkey" PRIMARY KEY ("id")
);

-- keep updated_at honest for the HUD's "last updated" line
CREATE OR REPLACE FUNCTION touch_timeline_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS "TimelineEvent_touch" ON "TimelineEvent";
CREATE TRIGGER "TimelineEvent_touch"
  BEFORE UPDATE ON "TimelineEvent"
  FOR EACH ROW EXECUTE FUNCTION touch_timeline_updated_at();

-- 2. SERVER TIME (lets clients correct for wrong phone clocks)
CREATE OR REPLACE FUNCTION get_server_time()
RETURNS TIMESTAMPTZ AS $$
BEGIN
  RETURN now();
END;
$$ LANGUAGE plpgsql STABLE;

-- 3. RLS — anyone can read, only BREEZE admins can write
ALTER TABLE "TimelineEvent" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TimelineAnnouncement" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "TimelineEvent: Public read" ON "TimelineEvent";
DROP POLICY IF EXISTS "TimelineEvent: Breeze admin insert" ON "TimelineEvent";
DROP POLICY IF EXISTS "TimelineEvent: Breeze admin update" ON "TimelineEvent";
DROP POLICY IF EXISTS "TimelineEvent: Breeze admin delete" ON "TimelineEvent";

CREATE POLICY "TimelineEvent: Public read" ON "TimelineEvent"
  FOR SELECT USING (true);
CREATE POLICY "TimelineEvent: Breeze admin insert" ON "TimelineEvent"
  FOR INSERT WITH CHECK (is_breeze_admin());
CREATE POLICY "TimelineEvent: Breeze admin update" ON "TimelineEvent"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "TimelineEvent: Breeze admin delete" ON "TimelineEvent"
  FOR DELETE USING (is_breeze_admin());

DROP POLICY IF EXISTS "TimelineAnnouncement: Public read" ON "TimelineAnnouncement";
DROP POLICY IF EXISTS "TimelineAnnouncement: Breeze admin insert" ON "TimelineAnnouncement";
DROP POLICY IF EXISTS "TimelineAnnouncement: Breeze admin update" ON "TimelineAnnouncement";
DROP POLICY IF EXISTS "TimelineAnnouncement: Breeze admin delete" ON "TimelineAnnouncement";

CREATE POLICY "TimelineAnnouncement: Public read" ON "TimelineAnnouncement"
  FOR SELECT USING (true);
CREATE POLICY "TimelineAnnouncement: Breeze admin insert" ON "TimelineAnnouncement"
  FOR INSERT WITH CHECK (is_breeze_admin());
CREATE POLICY "TimelineAnnouncement: Breeze admin update" ON "TimelineAnnouncement"
  FOR UPDATE USING (is_breeze_admin()) WITH CHECK (is_breeze_admin());
CREATE POLICY "TimelineAnnouncement: Breeze admin delete" ON "TimelineAnnouncement"
  FOR DELETE USING (is_breeze_admin());

-- Hero pick for overlapping live acts (admin-managed). Idempotent for
-- databases created before this column existed.
ALTER TABLE "TimelineEvent"
  ADD COLUMN IF NOT EXISTS "featured" BOOLEAN NOT NULL DEFAULT false;

-- 4. REALTIME so the HUD updates without refresh
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND tablename = 'TimelineEvent'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE "TimelineEvent";
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND tablename = 'TimelineAnnouncement'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE "TimelineAnnouncement";
  END IF;
END $$;

-- ============================================
-- DONE
-- ============================================
