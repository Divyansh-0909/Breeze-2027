-- Some installations already created this table through supabase_migration.sql.
-- Keep their existing submissions and policies when applying this migration.
CREATE TABLE IF NOT EXISTS "ContactSubmission" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    CONSTRAINT "ContactSubmission_pkey" PRIMARY KEY ("id")
);

-- The app reads and writes through Prisma on the server. Apply row security
-- on a fresh install as well, before any Supabase client policies are added.
ALTER TABLE "ContactSubmission" ENABLE ROW LEVEL SECURITY;
