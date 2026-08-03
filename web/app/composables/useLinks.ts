export type QrImageValue = string | null | 'generating'

export interface RedirectOut {
  redirect_id: string
  slug: string
  domain: string
  destination: string
  qr_image?: QrImageValue
  expired: boolean
  expired_on: string | null
  created_at: string
  visitor_count?: number
}

export interface CreateLinkBody {
  destination: string
  slug?: string
  domain?: string
  type?: string
  expired_on?: string
}

export interface TimeSeriesPoint {
  date: string
  visits: number
}

export interface CountryAnalytics {
  country: string
  visits: number
  percentage: number
}

export interface DeviceAnalytics {
  device: string
  visits: number
}

export interface VisitorLog {
  id: number
  ip: string
  location?: string | null
  device?: string | null
  created_at: string
}

export interface RedirectAnalyticsResponse {
  redirect_id: string
  domain: string
  slug?: string | null
  destination: string
  expired: boolean
  expired_on?: string | null
  created_at: string
  total_clicks: number
  unique_visitors: number
  top_country?: string | null
  top_device?: string | null
  chart_data: TimeSeriesPoint[]
  country_data: CountryAnalytics[]
  device_data: DeviceAnalytics[]
  recent_visitors: VisitorLog[]
}

export const useLinks = () => {
  const api = useApi()
  const toast = useToast()

  const links = useState<RedirectOut[]>('links.list', () => [])
  const pending = useState<boolean>('links.pending', () => false)
  const creating = useState<boolean>('links.creating', () => false)

  // ── Fetch all user links ───────────────────────────────────────────────────
  const fetchLinks = async () => {
    pending.value = true
    try {
      const res = await api<RedirectOut[]>('/api/v1/client/redirects', {
        cache: 'no-store'
      })
      links.value = res
    } catch (err: any) {
      const msg = err?.data?.detail || 'Failed to load links.'
      toast.add({ title: 'Error', description: msg, color: 'error' })
    } finally {
      pending.value = false
    }
  }

  // ── Fetch single link analytics ────────────────────────────────────────────
  const fetchAnalytics = async (redirectId: string, period = 'daily'): Promise<RedirectAnalyticsResponse | null> => {
    try {
      return await api<RedirectAnalyticsResponse>(`/api/v1/client/redirects/${redirectId}/analytics?period=${period}`)
    } catch (err: any) {
      const msg = err?.data?.detail || 'Failed to fetch link analytics.'
      toast.add({ title: 'Error', description: msg, color: 'error' })
      return null
    }
  }

  // ── Create short link ──────────────────────────────────────────────────────
  const createLink = async (body: CreateLinkBody): Promise<RedirectOut | null> => {
    creating.value = true
    try {
      const res = await api<RedirectOut>('/api/v1/client/create-short', {
        method: 'POST',
        body
      })
      links.value.unshift(res)
      toast.add({ title: 'Link created!', description: `/${res.slug}`, color: 'success' })
      return res
    } catch (err: any) {
      const msg = err?.data?.detail || 'Failed to create link.'
      toast.add({ title: 'Error', description: msg, color: 'error' })
      return null
    } finally {
      creating.value = false
    }
  }

  // ── Delete short link ──────────────────────────────────────────────────────
  const deleteLink = async (redirectId: string) => {
    try {
      await api(`/api/v1/client/redirects/${redirectId}`, { method: 'DELETE' })
      links.value = links.value.filter(l => l.redirect_id !== redirectId)
      toast.add({ title: 'Link deleted', color: 'success' })
    } catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to delete.', color: 'error' })
    }
  }

  // ── Copy short link to clipboard ───────────────────────────────────────────
  const copyLink = async (link: RedirectOut) => {
    const url = `https://${link.domain}/${link.slug}`
    await navigator.clipboard.writeText(url)
    toast.add({ title: 'Copied!', description: url, color: 'success', duration: 2000 })
  }

  const activeLinks = computed(() => links.value.filter(l => !l.expired))
  const expiredLinks = computed(() => links.value.filter(l => l.expired))
  const totalClicks = computed(() => links.value.reduce((sum, l) => sum + (l.visitor_count || 0), 0))

  return {
    links: readonly(links),
    pending: readonly(pending),
    creating: readonly(creating),
    activeLinks,
    expiredLinks,
    totalClicks,
    fetchLinks,
    fetchAnalytics,
    createLink,
    deleteLink,
    copyLink
  }
}
