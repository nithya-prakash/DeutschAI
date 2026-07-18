import { expect, test } from "@playwright/test";

// Requires the full stack running (docker compose up) and `npx playwright install`
// for browser binaries. Uses a randomized email so the test is repeatable against
// a persistent dev database.

test("a new user can register, log in, and see the dashboard", async ({ page }) => {
  const email = `e2e-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("E2E Test User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("supersecret123");
  await page.getByRole("button", { name: /create account/i }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Your dashboard", exact: true })).toBeVisible();
  await expect(page.getByText("Current streak")).toBeVisible();
});
