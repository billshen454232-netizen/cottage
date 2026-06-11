import { expect, test } from '@playwright/test';

const subscriptionUrl = 'https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml';

test('subscription workspace routes and copy action are connected', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/subscribe');

  await expect(page.locator('a[href="/"]')).toHaveCount(1);
  await expect(page.locator('a[href="/about"]')).toHaveCount(1);

  await expect(page.locator('.portal-nav a[href="#subscription"]')).toHaveCount(1);
  await expect(page.locator('.portal-nav a[href="#ip-activity"]')).toHaveCount(1);
  await expect(page.locator('.portal-nav a[href="#nodes"]')).toHaveCount(1);
  await expect(page.locator('.portal-nav a[href="#traffic"]')).toHaveCount(1);
  await expect(page.locator('.portal-nav a[href="#docs"]')).toHaveCount(1);

  await expect(page.locator('.action-panel')).not.toContainText(subscriptionUrl);

  await page.locator('#copyButton').click();
  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toBe(subscriptionUrl);

  await expect(page.locator(`.action-buttons a[href="${subscriptionUrl}"]`)).toHaveCount(1);
});
