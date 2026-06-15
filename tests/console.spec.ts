import { expect, test } from '@playwright/test';

test('console page opens and exit command returns home', async ({ page }) => {
  await page.goto('/about');

  const commandInput = page.locator('#consoleInput');
  await expect(commandInput).toBeAttached();

  await commandInput.fill('exit');
  await commandInput.press('Enter');

  await expect(page).toHaveURL('/');
});

test('console service and tool commands keep service links separate from scripts', async ({ page }) => {
  await page.goto('/about');

  await expect(page.locator('.subscription-module')).toHaveCount(0);

  const commandInput = page.locator('#consoleInput');
  await commandInput.fill('services');
  await commandInput.press('Enter');
  await expect(page.locator('.service-output a[href="/subscribe"]')).toHaveCount(1);

  await commandInput.fill('tools');
  await commandInput.press('Enter');
  await expect(page.locator('.tool-output a[href="/subscribe"]')).toHaveCount(0);
  await expect(page.locator('.tool-output a[href="https://subs.ttlink.asia/subs.html"]')).toHaveCount(0);
});
