import { expect, test } from '@playwright/test';

test('subscription workspace shows hidden subscription actions and IP activity', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/subscribe');

  await expect(page.getByRole('heading', { name: 'TTLINK' })).toBeVisible();
  await expect(page.getByText('STDIN | Subscribe >> /ops/workspace')).toBeVisible();
  await expect(page.getByRole('link', { name: '返回主站' })).toHaveAttribute('href', '/');
  await expect(page.getByRole('link', { name: '返回 Console' })).toHaveAttribute('href', '/about');

  await expect(page.getByRole('link', { name: /订阅/ })).toHaveAttribute('href', '#subscription');
  await expect(page.getByRole('link', { name: /IP 活动/ })).toHaveAttribute('href', '#ip-activity');
  await expect(page.getByRole('link', { name: /节点/ })).toHaveAttribute('href', '#nodes');
  await expect(page.getByRole('link', { name: /流量/ })).toHaveAttribute('href', '#traffic');
  await expect(page.getByRole('link', { name: /文档/ })).toHaveAttribute('href', '#docs');

  await expect(page.getByText('URL hidden')).toBeVisible();
  await expect(page.getByText('https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml')).toHaveCount(0);

  await expect(page.getByRole('heading', { name: 'IP 使用窗口' })).toBeVisible();
  await expect(page.getByText('192.168.1.24')).toBeVisible();
  await expect(page.getByText('China Mobile')).toBeVisible();
  await expect(page.getByText('AS9808')).toBeVisible();

  await page.getByRole('button', { name: '复制订阅' }).click();
  await expect(page.getByRole('button', { name: '已复制' })).toBeVisible();

  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toBe('https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml');

  await expect(page.getByRole('link', { name: '打开 YAML' })).toHaveAttribute(
    'href',
    'https://subs.ttlink.asia/subs/subs-ff5188e712b3ed8b.yaml',
  );
});
