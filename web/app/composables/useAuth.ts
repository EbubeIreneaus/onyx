export interface TierOut {
  tier_id: string
  name: string
  price: number
  permissions: string[]
  max_short_link: number
  is_active: boolean
}

export interface SubscriptionOut {
  sub_id: string
  amount: number
  status: string
  tier_id: string
  tier: TierOut | null
  created_at: string
  expired_at: string
}

export interface UserOut {
  id: number
  user_id: string
  fullname: string
  email: string
  status: string
  email_verified: boolean
  created_at: string
  current_subscription: SubscriptionOut | null
}

export const useAuth = () => {
  // useState must live inside the composable (needs Nuxt instance).
  // The string key means every call returns the same reactive ref — state is global.
  const user = useState<UserOut | null>('auth.user', () => null)
  const initialized = useState<boolean>('auth.initialized', () => false)
  const loading = useState<boolean>('auth.loading', () => false)

  const config = useRuntimeConfig()
  const router = useRouter()
  const toast = useToast()

  const apiBase = config.public.apiBase as string

  const isAuthenticated = computed(() => !!user.value)

  let restorePromise: Promise<void> | null = null

  // ── Restore session from refresh token cookie ──────────────────────────────
  const restore = async () => {
    if (initialized.value) return
    if (restorePromise) return restorePromise
    restorePromise = (async () => {
      try {
        const headers = import.meta.server ? (useRequestHeaders(['cookie']) as Record<string, string>) : undefined
        const res = await $fetch<{ success: boolean; token: string; refresh_token: string }>('/api/v1/auth/refresh-token', {
          method: 'POST',
          baseURL: apiBase,
          credentials: 'include',
          headers,
        })
        if (res?.success) {
          await fetchMe(headers)
        }
      }
      catch {
        user.value = null
      }
      finally {
        initialized.value = true
        restorePromise = null
      }
    })()
    return restorePromise
  }

  // ── Fetch current user profile ─────────────────────────────────────────────
  const fetchMe = async (customHeaders?: Record<string, string>) => {
    try {
      const headers = customHeaders || (import.meta.server ? (useRequestHeaders(['cookie']) as Record<string, string>) : undefined)
      const res = await $fetch<UserOut>('/api/v1/auth/me', {
        baseURL: apiBase,
        credentials: 'include',
        headers,
      })
      user.value = res
    }
    catch {
      user.value = null
    }
  }

  // ── Sign Up ────────────────────────────────────────────────────────────────
  const signup = async (fullname: string, email: string, password: string) => {
    loading.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/v1/auth/signup', {
        method: 'POST',
        baseURL: apiBase,
        credentials: 'include',
        body: { fullname, email, password },
      })
      if (res.success) {
        await fetchMe()
        await router.push('/dashboard')
      }
    }
    catch (err: any) {
      const msg = err?.data?.detail || 'Signup failed. Please try again.'
      toast.add({ title: 'Error', description: msg, color: 'error' })
      throw err
    }
    finally {
      loading.value = false
    }
  }

  // ── Sign In ────────────────────────────────────────────────────────────────
  const signin = async (email: string, password: string) => {
    loading.value = true
    try {
      const res = await $fetch<{ success: boolean }>('/api/v1/auth/signin', {
        method: 'POST',
        baseURL: apiBase,
        credentials: 'include',
        body: { email, password },
      })
      if (res.success) {
        await fetchMe()
        await router.push('/dashboard')
      }
    }
    catch (err: any) {
      const msg = err?.data?.detail || 'Invalid email or password.'
      toast.add({ title: 'Sign In Failed', description: msg, color: 'error' })
      throw err
    }
    finally {
      loading.value = false
    }
  }

  // ── Sign Out ───────────────────────────────────────────────────────────────
  const signout = async () => {
    try {
      await $fetch('/api/v1/auth/signout', {
        method: 'POST',
        baseURL: apiBase,
        credentials: 'include',
      })
    }
    catch { /* swallow */ }
    finally {
      user.value = null
      await router.push('/login')
    }
  }

  return {
    user: readonly(user),
    initialized: readonly(initialized),
    loading: readonly(loading),
    isAuthenticated,
    restore,
    fetchMe,
    signup,
    signin,
    signout,
  }
}
