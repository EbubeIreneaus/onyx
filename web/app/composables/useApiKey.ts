export interface ApiKeyData {
  api_key: string | null
  has_api_access: boolean
  created_at: string | null
}

export const useApiKey = () => {
  const api = useApi()
  const toast = useToast()

  const apiKeyData = useState<ApiKeyData | null>('apikey.data', () => null)
  const loading = useState<boolean>('apikey.loading', () => false)
  const generating = useState<boolean>('apikey.generating', () => false)

  const fetchApiKey = async () => {
    loading.value = true
    try {
      const res = await api<ApiKeyData>('/api/v1/client/api-key')
      apiKeyData.value = res
    } catch (err: any) {
      // ignore
    } finally {
      loading.value = false
    }
  }

  const generateApiKey = async () => {
    generating.value = true
    try {
      const res = await api<{ api_key: string, message: string }>('/api/v1/client/api-key/generate', {
        method: 'POST'
      })
      if (apiKeyData.value) {
        apiKeyData.value.api_key = res.api_key
        apiKeyData.value.created_at = new Date().toISOString()
      } else {
        apiKeyData.value = {
          api_key: res.api_key,
          has_api_access: true,
          created_at: new Date().toISOString()
        }
      }
      toast.add({ title: 'API Key Generated', description: res.message, color: 'success' })
      return res.api_key
    } catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to generate API key.', color: 'error' })
      return null
    } finally {
      generating.value = false
    }
  }

  const rotateApiKey = async () => {
    generating.value = true
    try {
      const res = await api<{ api_key: string, message: string }>('/api/v1/client/api-key/rotate', {
        method: 'POST'
      })
      if (apiKeyData.value) {
        apiKeyData.value.api_key = res.api_key
        apiKeyData.value.created_at = new Date().toISOString()
      }
      toast.add({ title: 'API Key Rotated', description: res.message, color: 'success' })
      return res.api_key
    } catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to rotate API key.', color: 'error' })
      return null
    } finally {
      generating.value = false
    }
  }

  const revokeApiKey = async () => {
    try {
      await api('/api/v1/client/api-key', { method: 'DELETE' })
      if (apiKeyData.value) {
        apiKeyData.value.api_key = null
        apiKeyData.value.created_at = null
      }
      toast.add({ title: 'API Key Revoked', color: 'success' })
    } catch (err: any) {
      toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to revoke key.', color: 'error' })
    }
  }

  return {
    apiKeyData: readonly(apiKeyData),
    loading: readonly(loading),
    generating: readonly(generating),
    fetchApiKey,
    generateApiKey,
    rotateApiKey,
    revokeApiKey
  }
}
