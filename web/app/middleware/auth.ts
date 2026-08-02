// Protect all /dashboard routes — redirect to /login if not authenticated
export default defineNuxtRouteMiddleware(async (_to) => {
  const { isAuthenticated, fetchUser } = useAuth()

  if (!isAuthenticated.value) {
    await fetchUser()
  }

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
