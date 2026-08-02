// Protect all /dashboard routes — await session initialization before redirecting
export default defineNuxtRouteMiddleware(async (_to) => {
  const { isAuthenticated, initialized, restore } = useAuth()

  if (!initialized.value) {
    await restore()
  }

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
