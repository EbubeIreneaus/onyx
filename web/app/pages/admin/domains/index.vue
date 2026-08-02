<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useSeoMeta({
  title: 'Manage Domains — Admin',
})

const api = useApi()
const toast = useToast()

interface AdminDomain {
  id: number
  name: str
  user_email: string
  txt_verified: boolean
  cname_verified: boolean
  is_root_domain: boolean
  created_at: string
}

const domains = ref<AdminDomain[]>([])
const loading = ref(true)
const searchQuery = ref('')

const fetchDomains = async () => {
  loading.value = true
  try {
    const params = searchQuery.value ? `?search=${encodeURIComponent(searchQuery.value)}` : ''
    domains.value = await api<AdminDomain[]>(`/api/v1/admin/domains${params}`)
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: 'Failed to load domains list', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDomains()
})

const handleForceVerify = async (d: AdminDomain) => {
  try {
    const res = await api<{ message: string }>(`/api/v1/admin/domains/${d.id}/force-verify`, {
      method: 'POST',
    })
    d.txt_verified = true
    d.cname_verified = true
    toast.add({ title: 'Domain Force-Verified', description: res.message, color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to force-verify domain', color: 'error' })
  }
}

const handleDeleteDomain = async (id: number) => {
  if (!confirm('Are you sure you want to delete this domain?')) return
  try {
    await api(`/api/v1/admin/domains/${id}`, { method: 'DELETE' })
    domains.value = domains.value.filter(d => d.id !== id)
    toast.add({ title: 'Domain Deleted', color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to delete domain', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-6 pb-12">
    <!-- Header & Search -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-white flex items-center gap-2">
          <UIcon name="i-lucide-globe" class="w-6 h-6 text-cyan-400" />
          Global Domain Management
        </h1>
        <p class="text-xs text-zinc-400 mt-1">View registered custom domains and trigger instant DNS force-verification.</p>
      </div>

      <div class="flex items-center gap-3">
        <UInput
          v-model="searchQuery"
          icon="i-lucide-search"
          placeholder="Search domain name..."
          class="w-64"
          @keyup.enter="fetchDomains"
        />
        <UButton color="neutral" variant="soft" icon="i-lucide-rotate-cw" @click="fetchDomains" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Domains Table -->
    <div v-else class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-zinc-300">
          <thead class="bg-zinc-950 text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
            <tr>
              <th class="py-3.5 px-4">Domain Name</th>
              <th class="py-3.5 px-4">Type</th>
              <th class="py-3.5 px-4">Owner Email</th>
              <th class="py-3.5 px-4">TXT DNS</th>
              <th class="py-3.5 px-4">CNAME DNS</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60 font-mono">
            <tr v-for="d in domains" :key="d.id" class="hover:bg-zinc-800/30 transition-colors">
              <!-- Name -->
              <td class="py-4 px-4 text-white font-bold">
                {{ d.name }}
              </td>

              <!-- Type -->
              <td class="py-4 px-4 font-sans">
                <UBadge
                  :color="d.is_root_domain ? 'primary' : 'info'"
                  variant="soft"
                  size="xs"
                  :label="d.is_root_domain ? 'Root Domain' : 'Subdomain'"
                />
              </td>

              <!-- Owner -->
              <td class="py-4 px-4 text-zinc-400">
                {{ d.user_email }}
              </td>

              <!-- TXT Status -->
              <td class="py-4 px-4 font-sans">
                <UBadge
                  :color="d.txt_verified ? 'success' : 'neutral'"
                  variant="soft"
                  size="xs"
                  :label="d.txt_verified ? 'Verified' : 'Pending'"
                />
              </td>

              <!-- CNAME Status -->
              <td class="py-4 px-4 font-sans">
                <UBadge
                  :color="d.cname_verified ? 'success' : 'neutral'"
                  variant="soft"
                  size="xs"
                  :label="d.cname_verified ? 'Verified' : 'Pending'"
                />
              </td>

              <!-- Actions -->
              <td class="py-4 px-4 text-right space-x-2 font-sans">
                <UButton
                  v-if="!d.txt_verified || !d.cname_verified"
                  color="warning"
                  variant="soft"
                  size="xs"
                  icon="i-lucide-check-circle"
                  @click="handleForceVerify(d)"
                >
                  Force Verify
                </UButton>

                <UButton
                  color="error"
                  variant="soft"
                  size="xs"
                  icon="i-lucide-trash-2"
                  @click="handleDeleteDomain(d.id)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
