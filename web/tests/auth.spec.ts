import { test, expect } from '@playwright/test'

test('signup and login flow works', async ({ page }) => {
  const email = `playwright-${Date.now()}@example.com`

  await page.goto('/signup')
  await page.getByLabel(/full name/i).fill('Playwright User')
  await page.getByLabel(/email address/i).fill(email)
  await page.getByLabel(/password/i).fill('StrongPass123')
  await page.getByLabel(/confirm password/i).fill('StrongPass123')
  await page.getByRole('button', { name: /create account/i }).click()

  await expect(page).toHaveURL(/\/dashboard/) 
  await page.goto('/login')
  await page.getByLabel(/email/i).fill(email)
  await page.getByLabel(/password/i).fill('StrongPass123')
  await page.getByRole('button', { name: /sign in/i }).click()

  await expect(page).toHaveURL(/\/dashboard/)
})
