import { test, expect } from '@playwright/test'

test('signup and login flow works', async ({ page }) => {
  const email = `playwright-${Date.now()}@example.com`

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const url = request.url()
    const origin = request.headers()['origin'] || 'http://127.0.0.1:3000'

    const corsHeaders = {
      'access-control-allow-origin': origin,
      'access-control-allow-credentials': 'true',
      'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'access-control-allow-headers': 'Content-Type, Authorization, Cookie',
    }

    if (request.method() === 'OPTIONS') {
      return route.fulfill({
        status: 204,
        headers: corsHeaders,
      })
    }

    if (url.includes('/api/v1/auth/signup') || url.includes('/api/v1/auth/signin')) {
      return route.fulfill({
        status: 200,
        headers: corsHeaders,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      })
    }

    if (url.includes('/api/v1/auth/me')) {
      return route.fulfill({
        status: 200,
        headers: corsHeaders,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          user_id: 'usr_test',
          fullname: 'Playwright User',
          email,
          status: 'active',
          email_verified: true,
          created_at: new Date().toISOString(),
          current_subscription: null,
        }),
      })
    }

    return route.fulfill({
      status: 200,
      headers: corsHeaders,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  // 1. Signup Flow
  await page.goto('/signup')
  await page.getByPlaceholder('Jane Doe').fill('Playwright User')
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('At least 8 characters').fill('StrongPass123')
  await page.getByPlaceholder('Repeat your password').fill('StrongPass123')

  await page.locator('form').evaluate((form: HTMLFormElement) => {
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
  })

  await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 })

  // 2. Login Flow
  await page.goto('/login')
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('••••••••').fill('StrongPass123')

  await page.locator('form').evaluate((form: HTMLFormElement) => {
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
  })

  await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 })
})

