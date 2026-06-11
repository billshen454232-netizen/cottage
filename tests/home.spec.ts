import { expect, test } from '@playwright/test';

test('homepage entry links route to the app sections', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('nav[aria-label="服务入口"] a')).toHaveCount(4);
  await expect(page.locator('nav[aria-label="服务入口"] a').first()).toHaveAttribute('href', '/subscribe');
  await expect(page.locator('a.console-link')).toHaveAttribute('href', '/about');
});
