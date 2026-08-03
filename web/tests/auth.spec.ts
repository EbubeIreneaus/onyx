import { test, expect, type Page } from '@playwright/test'

const API_HOSTS = ['http://localhost:8000', 'http://127.0.0.1:8000']

async function mockApiRoutes(page: Page, email: string) {
  let isLoggedIn = false

  const corsHeaders = {
    'access-control-allow-origin': 'http://localhost:3000',
    'access-control-allow-credentials': 'true',
    'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'access-control-allow-headers': 'Content-Type, Authorization, Cookie'
  }

  const mockUser = {
    id: 1,
    user_id: 'usr_test',
    fullname: 'Playwright User',
    email,
    status: 'active',
    email_verified: true,
    created_at: new Date().toISOString(),
    current_subscription: null
  }

  for (const host of API_HOSTS) {
    await page.route(`${host}/**`, async (route) => {
      const url = route.request().url()
      const method = route.request().method()

      if (method === 'OPTIONS') {
        return route.fulfill({ status: 204, headers: corsHeaders })
      }
      if (url.includes('/api/v1/auth/signup') || url.includes('/api/v1/auth/signin')) {
        isLoggedIn = true
        return route.fulfill({
          status: 200,
          headers: corsHeaders,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        })
      }
      if (url.includes('/api/v1/auth/me') || url.includes('/api/v1/auth/refresh-token')) {
        if (!isLoggedIn) {
          return route.fulfill({
            status: 401,
            headers: corsHeaders,
            contentType: 'application/json',
            body: JSON.stringify({ detail: 'Unauthenticated' })
          })
        }
        return route.fulfill({
          status: 200,
          headers: corsHeaders,
          contentType: 'application/json',
          body: JSON.stringify(url.includes('/refresh-token') ? { success: true } : mockUser)
        })
      }
      return route.fulfill({
        status: 200,
        headers: corsHeaders,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })
  }
}

test('signup flow works', async ({ page }) => {
  await page.context().clearCookies()

  const email = `playwright-${Date.now()}@example.com`
  await mockApiRoutes(page, email)

  await page.goto('http://localhost:3000/signup')

  await page.waitForLoadState('networkidle')

  await page.getByTestId('fullname').fill('Playwright User')
  await page.getByTestId('email').fill(email)
  await page.getByTestId('password').fill('StrongPass123')
  await page.getByTestId('confirm-password').fill('StrongPass123')

  // User added test-id="submit-btn" to the UButton — use it for reliable clicking
  await page.getByTestId('submit-btn').click()

  await expect(page).toHaveURL('http://localhost:3000/dashboard')
})

test('login flow works', async ({ page }) => {
  const email = `playwright-${Date.now()}@example.com`
  await mockApiRoutes(page, email)

  await page.goto('/login')

  await page.waitForLoadState('networkidle')

  await page.getByTestId('email').fill(email)
  await page.getByTestId('password').fill('StrongPass123')

  await page.getByTestId('submit-btn').click()

  await page.waitForURL(/\/dashboard/, { timeout: 15000 })
  await expect(page).toHaveURL(/\/dashboard/)
})
