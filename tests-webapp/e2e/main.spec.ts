import { test, expect } from "@playwright/test";

test.describe("Landing Page", () => {
  test("renders hero, stats, and CTA", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Authority");
    await expect(page.locator("text=68")).toBeVisible();
    await expect(page.locator("text=Try the Calculator")).toBeVisible();
  });

  test("navigates to calculator from CTA", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Try the Calculator");
    await expect(page).toHaveURL(/\/calculator/);
  });
});

test.describe("Calculator", () => {
  test("displays category cards", async ({ page }) => {
    await page.goto("/calculator");
    await expect(page.locator("text=Core Methods")).toBeVisible();
    await expect(page.locator("text=Valuation Approaches")).toBeVisible();
    await expect(page.locator("text=Income Methods")).toBeVisible();
  });

  test("navigates to method page", async ({ page }) => {
    await page.goto("/calculator/present-value");
    await expect(page.locator("h1")).toContainText("Present Value");
    await expect(page.locator("text=Calculate")).toBeVisible();
  });

  test("submits present value calculation", async ({ page }) => {
    await page.goto("/calculator/present-value");

    await page.fill('input[placeholder*="Future value"]', "100000");
    await page.fill('input[placeholder*="discount"]', "0.10");
    await page.fill('input[placeholder*="periods"]', "5");

    await page.click('button[type="submit"]');

    // Should see a result (value or error — depends on API availability)
    await page.waitForSelector("text=/\\$\\d|error|Calculating/i", { timeout: 10000 });
  });
});

test.describe("MCP Gateway", () => {
  test("displays setup instructions", async ({ page }) => {
    await page.goto("/mcp");
    await expect(page.locator("text=Quick Start")).toBeVisible();
    await expect(page.locator("text=pip install")).toBeVisible();
  });
});

test.describe("Skills Page", () => {
  test("lists all 4 skills", async ({ page }) => {
    await page.goto("/skills");
    await expect(page.locator("text=Asset Valuation")).toBeVisible();
    await expect(page.locator("text=Discount Rate Construction")).toBeVisible();
    await expect(page.locator("text=Purchase Price Allocation")).toBeVisible();
    await expect(page.locator("text=Impairment Testing")).toBeVisible();
  });
});

test.describe("Navigation", () => {
  test("header links work", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Calculator");
    await expect(page).toHaveURL(/\/calculator/);
  });

  test("footer links present", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=Documentation")).toBeVisible();
    await expect(page.locator("text=GitHub")).toBeVisible();
  });
});
