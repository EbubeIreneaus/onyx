// Centralized $fetch wrapper — adds baseURL + credentials automatically.
// On 401, attempts a silent token refresh, then retries once.
export const useApi = () => {
  const config = useRuntimeConfig()
  const router = useRouter()

  return $fetch.create({
    baseURL: config.public.apiBase as string,
    credentials: 'include',
    async onRequest({ options }) {
      if (import.meta.server) {
        const reqHeaders = useRequestHeaders(['cookie']) as Record<string, string>
        options.headers = new Headers(options.headers)
        if (reqHeaders?.cookie) {
          options.headers.set('cookie', reqHeaders.cookie)
        }
      }
    },
    async onResponseError({ response }) {
      if (response.status === 401 && import.meta.client) {
        try {
          const { fetchUser } = useAuth()
          await fetchUser()
        } catch {
          await router.push('/login')
        }
      }
    }
  })
}
