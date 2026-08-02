export interface DomainOut {
  id: number
  name: string
  user_id: string
  txt_verified: boolean
  cname_verified: boolean
  txt_token?: string | null
  created_at: string
}

export interface CreateDomainBody {
  name: string
}

export interface DomainCheckResult {
  available: boolean
  registered: boolean
  owned_by_user: boolean
  txt_verified: boolean
  cname_verified: boolean
  domain_id: number | null
  message: string
  txt_verification_token?: string | null
}

export const useDomains = () => {
  const api = useApi()
  const toast = useToast()

  const domains = useState<DomainOut[]>('domains.list', () => [])
  const pending = useState<boolean>('domains.pending', () => false)

  const fetchDomains = async () => {
    pending.value = true
    try {
      const res = await api<DomainOut[]>('/api/v1/client/domains')
      domains.value = res
    }
    catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to load domains.', color: 'error' })
    }
    finally {
      pending.value = false
    }
  }

  const fetchDomainById = async (id: number): Promise<DomainOut | null> => {
    try {
      const res = await api<DomainOut>(`/api/v1/client/domains/${id}`)
      return res
    }
    catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Domain not found.', color: 'error' })
      return null
    }
  }

  const checkDomain = async (domain: string, slug?: string): Promise<DomainCheckResult | null> => {
    try {
      const res = await api<DomainCheckResult>('/api/v1/client/check-domain', {
        method: 'POST',
        body: { domain, slug },
      })
      return res
    }
    catch (err: any) {
      return null
    }
  }

  const createDomain = async (body: CreateDomainBody): Promise<DomainOut | null> => {
    try {
      const res = await api<DomainOut>('/api/v1/client/create-domain', {
        method: 'POST',
        body,
      })
      domains.value.unshift(res)
      toast.add({ title: 'Domain registered!', description: body.name, color: 'success' })
      return res
    }
    catch (err: any) {
      const msg = err?.data?.detail || 'Failed to register domain.'
      toast.add({ title: 'Error', description: msg, color: 'error' })
      return null
    }
  }

  const deleteDomain = async (domainId: number) => {
    try {
      await api(`/api/v1/client/domains/${domainId}`, { method: 'DELETE' })
      domains.value = domains.value.filter(d => d.id !== domainId)
      toast.add({ title: 'Domain removed', color: 'success' })
    }
    catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to delete.', color: 'error' })
    }
  }

  const verifiedDomains = computed(() => domains.value.filter(d => d.txt_verified))
  const pendingDomains = computed(() => domains.value.filter(d => !d.txt_verified))

  return {
    domains: readonly(domains),
    pending: readonly(pending),
    verifiedDomains,
    pendingDomains,
    fetchDomains,
    fetchDomainById,
    checkDomain,
    createDomain,
    deleteDomain,
  }
}
