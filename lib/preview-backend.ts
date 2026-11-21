export function hasIsolatedPreviewBackend(env: Readonly<Record<string, string | undefined>> = process.env) {
  if (env.GULLYVERSE_RUNTIME_PREVIEW !== "1" || env.GULLYVERSE_ISOLATED_TEST_BACKEND !== "1") return false;
  try {
    const database = new URL(env.DATABASE_URL ?? "");
    return ["postgres:", "postgresql:"].includes(database.protocol) &&
      ["localhost", "127.0.0.1", "[::1]"].includes(database.hostname) &&
      /^\/breeze_runtime_tests(?:_[a-z0-9]+)*$/.test(database.pathname);
  } catch {
    return false;
  }
}
