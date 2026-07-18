import { expect, test } from "@playwright/test";

// Requires the full stack running (docker compose up) and `npx playwright install`.
// Covers the access-control-denial path: a regular (non-superuser) account is the
// one every fresh registration produces, so this is the deterministic case to test
// in E2E without seeding a superuser account.

test("a regular user does not see the Admin nav item and is redirected away from /admin", async ({
  page,
}) => {
  const email = `e2e-admin-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("E2E Regular User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("supersecret123");
  await page.getByRole("button", { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await expect(page.getByRole("link", { name: "Admin" })).not.toBeVisible();

  await page.goto("/admin");
  await expect(page).toHaveURL(/\/dashboard$/);
});
