import { expect, test } from "@playwright/test";

// Requires the full stack running (docker compose up) and `npx playwright install`.

test("logging a session updates the streak and minutes", async ({ page }) => {
  const email = `e2e-dashboard-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("E2E Dashboard User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("supersecret123");
  await page.getByRole("button", { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByLabel("Minutes studied").fill("45");
  await page.getByRole("button", { name: /log today/i }).click();

  await expect(page.getByText("Session logged")).toBeVisible();
  await expect(page.getByText("1 d", { exact: false }).first()).toBeVisible();
});
