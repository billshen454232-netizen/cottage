import { expect, test } from '@playwright/test';

test('console page opens and exit command returns home', async ({ page }) => {
  await page.goto('/about');

  const commandInput = page.getByRole('textbox', { name: 'Console command' });
  await expect(commandInput).toBeVisible();

  await commandInput.fill('exit');
  await commandInput.press('Enter');

  await expect(page).toHaveURL('/');
});
