-- CreateEnum
CREATE TYPE "event_category" AS ENUM ('Cultural', 'Technical');

-- CreateEnum
CREATE TYPE "accommodation_option" AS ENUM ('DAY1', 'DAY2', 'DAY3');

-- CreateTable
CREATE TABLE "EventItem" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "event_name" TEXT NOT NULL DEFAULT '',
    "event_description" TEXT NOT NULL DEFAULT '',
    "event_price" SMALLINT NOT NULL,
    "event_org" TEXT,
    "event_venue" TEXT,
    "event_date" TEXT,
    "image_url" TEXT,
    "event_type" "event_category",
    "registration_open" BOOLEAN NOT NULL DEFAULT true,
    "event_end_date" TEXT,
    "event_pair_price" SMALLINT,

    CONSTRAINT "EventItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MerchItem" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "product_name" TEXT NOT NULL,
    "product_price" SMALLINT NOT NULL DEFAULT 0,
    "product_description" TEXT NOT NULL DEFAULT '',
    "image_url" TEXT,

    CONSTRAINT "MerchItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PendingTransaction" (
    "id" TEXT NOT NULL,
    "amount" BIGINT NOT NULL,
    "time" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "cart" JSONB NOT NULL,
    "accommodation" "accommodation_option"[],
    "accommodation_price" BIGINT NOT NULL,

    CONSTRAINT "PendingTransaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SubmittedTransaction" (
    "token" VARCHAR NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    "accommodation" "accommodation_option"[],
    "accommodation_price" BIGINT NOT NULL,
    "student_details" TEXT,

    CONSTRAINT "SubmittedTransaction_pkey" PRIMARY KEY ("token")
);

-- CreateTable
CREATE TABLE "ConfirmedEvent" (
    "token" VARCHAR NOT NULL,
    "id" UUID NOT NULL,
    "quantity" BIGINT NOT NULL DEFAULT 0,

    CONSTRAINT "confirmedEvent_pkey" PRIMARY KEY ("token","id")
);

-- CreateTable
CREATE TABLE "ConfirmedMerch" (
    "token" VARCHAR NOT NULL,
    "id" UUID NOT NULL,
    "size" TEXT NOT NULL DEFAULT '',
    "quantity" BIGINT NOT NULL DEFAULT 0,

    CONSTRAINT "ConfirmedMerch_pkey" PRIMARY KEY ("token","id","size")
);

-- CreateTable
CREATE TABLE "Roles" (
    "id" UUID NOT NULL,
    "club_name" TEXT NOT NULL DEFAULT '',
    "email" TEXT NOT NULL DEFAULT '',

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ContactSubmission" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "message" TEXT NOT NULL,

    CONSTRAINT "ContactSubmission_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "ConfirmedEvent" ADD CONSTRAINT "confirmedEvent_id_fkey" FOREIGN KEY ("id") REFERENCES "EventItem"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ConfirmedEvent" ADD CONSTRAINT "confirmedEvent_token_fkey" FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ConfirmedMerch" ADD CONSTRAINT "confirmedMerch_id_fkey" FOREIGN KEY ("id") REFERENCES "MerchItem"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ConfirmedMerch" ADD CONSTRAINT "confirmedMerch_token_fkey" FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE CASCADE ON UPDATE CASCADE;
