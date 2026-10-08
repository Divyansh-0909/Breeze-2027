import { Prisma } from "@prisma/client";

export const eventCatalogUnavailableMessage = "Event listings are currently unavailable. Please try again later.";

type CatalogRead<T> = { available: true; data: T } | { available: false; data: null };
const connectionErrors = new Set(["P1000", "P1001", "P1002", "P1003", "P1008", "P1010", "P1011", "P1017", "P2024"]);

/** Keep an unavailable catalog distinct from a successful empty or missing result. */
export async function readEventCatalog<T>(read: () => Promise<T>): Promise<CatalogRead<T>> {
  try {
    return { available: true, data: await read() };
  } catch (error) {
    if ((error instanceof Prisma.PrismaClientInitializationError &&
         (!error.errorCode || connectionErrors.has(error.errorCode))) ||
        (error instanceof Prisma.PrismaClientKnownRequestError && connectionErrors.has(error.code))) {
      return { available: false, data: null };
    }
    // Query validation, coded schema errors and unrelated exceptions retain
    // their existing error behavior instead of masquerading as an empty catalog.
    throw error;
  }
}
