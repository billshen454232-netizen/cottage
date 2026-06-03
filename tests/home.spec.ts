import { expect, test } from '@playwright/test';

const expectedServices = ['订阅门户', 'CLI Proxy API', '个人博客', '知识图谱'];

test('homepage shows the command center and service links', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'TTLINK Command Center' })).toBeVisible();

  for (const serviceName of expectedServices) {
    await expect(page.getByRole('link', { name: new RegExp(serviceName) })).toBeVisible();
  }

  await expect(page.getByRole('link', { name: /订阅门户/ })).toHaveAttribute(
    'href',
    'https://subs.ttlink.asia/subs.html',
  );
  await expect(page.getByRole('link', { name: /CLI Proxy API/ })).toHaveAttribute(
    'href',
    'https://cli.ttlink.asia/management.html',
  );
});
