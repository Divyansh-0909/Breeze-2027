import { PrismaClient } from "@prisma/client";

const globalForPrisma = global as unknown as { prisma: PrismaClient };

function getNormalizedUrl(): string | undefined {
  const url = process.env.DATABASE_URL;
  if (!url) return undefined;

  let normalized = url.trim().replace(/^['"]|['"]$/g, "");
  // Normalize pgbouncer flag if incomplete
  if (normalized.includes("?pgbouncer") && !normalized.includes("pgbouncer=")) {
    normalized = normalized.replace("?pgbouncer", "?pgbouncer=true");
  }
  // Ensure connect_timeout=30 is included to avoid premature timeouts on cold Supabase poolers
  if (!normalized.includes("connect_timeout")) {
    normalized += (normalized.includes("?") ? "&" : "?") + "connect_timeout=30";
  }
  return normalized;
}

const dbUrl = getNormalizedUrl();

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    datasources: dbUrl ? { db: { url: dbUrl } } : undefined,
    log: process.env.NODE_ENV === "development" ? ["warn", "error"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
