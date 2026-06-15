import { expect, test } from '@playwright/test';

const subscriptionUrl = 'https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml';

test('copy button writes subscription URL to clipboard', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/subscribe');

  const copyButton = page.locator('#copyButton');
  await expect(copyButton).toBeVisible();

  await copyButton.click();

  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toBe(subscriptionUrl);
  await expect(copyButton).toHaveText('已复制');
});

test('subscription page can fetch status JSON', async ({ page }) => {
  const statusResponsePromise = page.waitForResponse((response) => {
    const url = response.url();

    return (
      response.ok() &&
      (url.endsWith('subscription-status.sample.json') ||
        url.endsWith('subscription-status.json'))
    );
  });

  await page.goto('/subscribe');

  const statusResponse = await statusResponsePromise;
  const statusData = await statusResponse.json();

  expect(statusData).toHaveProperty('version');
  expect(statusData).toHaveProperty('generatedAt');
  expect(statusData).toHaveProperty('subscription');
});