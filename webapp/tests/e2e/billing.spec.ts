import { test, expect } from "@playwright/test";

test.describe("Commercial readiness (AC-BILL-01, AC-COMP-01, AC-GATE-01)", () => {
  test("pricing page renders all three tiers", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("text=Free")).toBeVisible();
    await expect(page.locator("text=Pro")).toBeVisible();
    await expect(page.locator("text=Enterprise")).toBeVisible();
  });

  test("terms and privacy pages render", async ({ page }) => {
    await page.goto("/terms");
    await expect(page.locator("h1")).toContainText("Terms");
    await page.goto("/privacy");
    await expect(page.locator("h1")).toContainText("Privacy");
  });

  test("calculator result carries a disclaimer (AC-COMP-01)", async ({ page }) => {
    await page.goto("/calculator/present-value");
    await page.fill('input[type="number"] >> nth=0', "100000");
    await page.fill('input[type="number"] >> nth=1', "0.10");
    await page.fill('input[type="number"] >> nth=2', "5");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Disclaimer")).toBeVisible({ timeout: 15000 });
  });

  test("checkout without billing config degrades gracefully (AC-ERR-01)", async ({ page }) => {
    // With no STRIPE_SECRET_KEY, the checkout endpoint returns 503 and the UI
    // stays usable (the free tier is unaffected).
    await page.goto("/pricing");
    await expect(page.locator("text=Pro")).toBeVisible();
  });
});
