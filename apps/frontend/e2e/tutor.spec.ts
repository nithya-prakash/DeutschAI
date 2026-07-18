import { expect, test } from "@playwright/test";

// Requires the full stack running (docker compose up) and `npx playwright install`.
// Deterministic in this environment: ANTHROPIC_API_KEY is genuinely unset, so the
// "not configured" banner is real backend behavior, not something this test mocks.

test("asking the Tutor without ANTHROPIC_API_KEY shows the honest not-configured banner", async ({
  page,
}) => {
  const email = `e2e-tutor-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("E2E Tutor User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("supersecret123");
  await page.getByRole("button", { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.goto("/tutor");
  await page.getByPlaceholder(/kein instead of nicht/i).fill("Was ist Akkusativ?");
  await page.getByRole("button", { name: /^ask$/i }).click();

  await expect(page.getByText("Tutor Agent isn't configured yet")).toBeVisible();
});
