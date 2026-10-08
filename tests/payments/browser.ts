import { chromium, Page } from "playwright";
import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";

async function main() {
  const artifactDir = process.env.PAYMENT_TEST_ARTIFACT_DIR || ".payment-test-artifacts";
  await mkdir(artifactDir, { recursive: true });
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  let lastPage: Page;
  const errors: string[] = [];
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    lastPage = page;
    const mutations: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("request", request => { if (/\/api\/(pay|checkout|breeze-admin)/.test(request.url())) mutations.push(request.url()); });
    await page.route("**/api/**", route => {
      if (!["GET", "HEAD"].includes(route.request().method())) {
        mutations.push(`${route.request().method()} ${route.request().url()}`);
        return route.abort();
      }
      return route.continue();
    });
    const base = process.env.PAYMENT_TEST_URL || "http://127.0.0.1:3000";
    await page.goto(`${base}/payments/preview`, { waitUntil: "domcontentloaded" });
    await page.getByRole("heading", { name: "Save your place. Make it official." }).waitFor();
    assert.equal(await page.getByAltText("Non-payment preview QR").count(), 0);
    await page.getByLabel("Full name", { exact: true }).fill("Example Student");
    await page.getByLabel("Email for confirmation").fill("example@example.invalid");
    await page.getByLabel("Phone number", { exact: true }).fill("9876543210");
    await page.getByLabel("College roll number").fill("TEST123");
    await page.getByLabel("College and graduation year").fill("Example College, 2027");
    await page.getByRole("button", { name: "Save details and show payment QR" }).click();
    await page.getByAltText("Non-payment preview QR").waitFor();
    await page.screenshot({ path: `${artifactDir}/customer-mobile.png`, fullPage: true });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    await page.getByRole("button", { name: "I've paid — submit for verification" }).click();
    await page.getByText("Awaiting bank verification", { exact: true }).waitFor();
    await page.goto(`${base}/payments/admin-preview`, { waitUntil: "domcontentloaded" });
    await page.getByRole("heading", { name: "Bank statement matching" }).waitFor();
    await page.getByRole("button", { name: "Load sample statement" }).click();
    await page.getByRole("button", { name: "Validate mapped rows" }).click();
    await page.getByLabel("This is the bank statement", { exact: false }).check();
    await page.getByLabel("I checked all extracted rows", { exact: false }).check();
    await page.getByRole("button", { name: "Import and automatically match payments" }).click();
    await page.getByText("Statement already imported", { exact: true }).waitFor();
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
    await page.screenshot({ path: `${artifactDir}/admin-mobile.png`, fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: `${artifactDir}/admin-desktop.png`, fullPage: true });
    assert.deepEqual(errors, []);
    assert.deepEqual(mutations, []);
    console.log("PASS: customer saves details before seeing QR, pending status, statement mapping/import preview, mobile overflow, and zero preview API mutations");
  } catch (error) {
    console.log({ pageErrors: errors, url: lastPage?.url(), text: (await lastPage?.locator("body").innerText())?.slice(0, 3000) });
    if (lastPage) await lastPage.screenshot({ path: `${artifactDir}/browser-failure.png`, fullPage: true });
    throw error;
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
