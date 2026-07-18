import { expect, test } from "@playwright/test";

// Requires the full stack running (docker compose up) and `npx playwright install`.

test("adding a word and reviewing it moves it off the due list", async ({ page }) => {
  const email = `e2e-vocab-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("E2E Vocab User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("supersecret123");
  await page.getByRole("button", { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.goto("/vocabulary");
  await page.getByLabel("German").fill("der Tisch");
  await page.getByLabel("English").fill("the table");
  await page.getByRole("button", { name: /add word/i }).click();

  const row = page.getByRole("row", { name: /der Tisch/i });
  await expect(row.getByText("Due")).toBeVisible();

  await row.getByRole("button", { name: "Good" }).click();
  await expect(row.getByText("Due")).not.toBeVisible();
});
