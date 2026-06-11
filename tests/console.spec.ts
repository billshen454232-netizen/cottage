import { expect, test } from '@playwright/test';

test('console page opens and exit command returns home', async ({ page }) => {
  await page.goto('/about');

  const commandInput = page.getByRole('textbox', { name: 'Console command' });
  await expect(commandInput).toBeVisible();

  await commandInput.fill('exit');
  await commandInput.press('Enter');

  await expect(page).toHaveURL('/');
});

test('console exposes subscription center entry and command', async ({ page }) => {
  await page.goto('/about');

  await expect(page.getByLabel('Subscription Center module')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Open Workspace' })).toHaveAttribute('href', '/subscribe');

  const commandInput = page.getByRole('textbox', { name: 'Console command' });
  await commandInput.fill('subscribe');
  await commandInput.press('Enter');

  await expect(page.getByText('Open Subscription Workspace')).toBeVisible();
});

test('tools command points subscription portal to local workspace', async ({ page }) => {
  await page.goto('/about');

  const commandInput = page.getByRole('textbox', { name: 'Console command' });
  await commandInput.fill('tools');
  await commandInput.press('Enter');

  await expect(page.getByRole('link', { name: 'Subs Portal' })).toHaveAttribute('href', '/subscribe');
  await expect(page.getByText('https://subs.ttlink.asia/subs.html')).toHaveCount(0);
});
