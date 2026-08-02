// Plugin to restore auth session on initial load
export default defineNuxtPlugin(async () => {
  const { isAuthenticated, fetchUser } = useAuth()
  if (!isAuthenticated.value) {
    await fetchUser()
  }
})
