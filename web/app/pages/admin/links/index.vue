<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useSeoMeta({
  title: 'Manage Short Links — Admin',
})

const api = useApi()
const toast = useToast()

interface AdminRedirect {
  id: string
  domain: string
  slug: string
  destination: string
  visits: number
  expired: boolean
  user_email: string
  created_at: string
}

const redirects = ref<AdminRedirect[]>([])
const loading = ref(true)
const searchQuery = ref('')

const fetchRedirects = async () => {
  loading.value = true
  try {
    const params = searchQuery.value ? `?search=${encodeURIComponent(searchQuery.value)}` : ''
    redirects.value = await api<AdminRedirect[]>(`/api/v1/admin/redirects${params}`)
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: 'Failed to load redirects list', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRedirects()
})

const toggleLinkStatus = async (r: AdminRedirect) => {
  const nextExpired = !r.expired
  try {
    await api(`/api/v1/admin/redirects/${r.id}/status?expired=${nextExpired}`, {
      method: 'PATCH',
    })
    r.expired = nextExpired
    toast.add({ title: `Link ${nextExpired ? 'disabled' : 'enabled'} successfully`, color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to update status', color: 'error' })
  }
}

const handleDeleteLink = async (id: string) => {
  if (!confirm('Are you sure you want to delete this short link?')) return
  try {
    await api(`/api/v1/admin/redirects/${id}`, { method: 'DELETE' })
    redirects.value = redirects.value.filter(r => r.id !== id)
    toast.add({ title: 'Short Link Deleted', color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to delete link', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-6 pb-12">
    <!-- Header & Search -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-white flex items-center gap-2">
          <UIcon name="i-lucide-link" class="w-6 h-6 text-indigo-400" />
          Short Link Moderation
        </h1>
        <p class="text-xs text-zinc-400 mt-1">Search, inspect destination URLs, disable suspicious links, or delete records.</p>
      </div>

      <div class="flex items-center gap-3">
        <UInput
          v-model="searchQuery"
          icon="i-lucide-search"
          placeholder="Search slug, domain, or destination..."
          class="w-64"
          @keyup.enter="fetchRedirects"
        />
        <UButton color="neutral" variant="soft" icon="i-lucide-rotate-cw" @click="fetchRedirects" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Links Table -->
    <div v-else class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-zinc-300">
          <thead class="bg-zinc-950 text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
            <tr>
              <th class="py-3.5 px-4">Short URL</th>
              <th class="py-3.5 px-4">Target Destination</th>
              <th class="py-3.5 px-4">Owner Email</th>
              <th class="py-3.5 px-4">Visits</th>
              <th class="py-3.5 px-4">Status</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60 font-mono">
            <tr v-for="r in redirects" :key="r.id" class="hover:bg-zinc-800/30 transition-colors">
              <!-- Short URL -->
              <td class="py-4 px-4 font-bold text-emerald-400">
                {{ r.domain }}/{{ r.slug }}
              </td>

              <!-- Destination -->
              <td class="py-4 px-4 max-w-xs truncate text-zinc-300" :title="r.destination">
                {{ r.destination }}
              </td>

              <!-- Owner -->
              <td class="py-4 px-4 text-zinc-400 font-sans">
                {{ r.user_email }}
              </td>

              <!-- Visits -->
              <td class="py-4 px-4 font-bold text-white">
                {{ r.visits }}
              </td>

              <!-- Status -->
              <td class="py-4 px-4 font-sans">
                <UBadge
                  :color="r.expired ? 'error' : 'success'"
                  variant="soft"
                  size="xs"
                  :label="r.expired ? 'Disabled' : 'Active'"
                />
              </td>

              <!-- Actions -->
              <td class="py-4 px-4 text-right space-x-2 font-sans">
                <UButton
                  :to="`/dashboard/redirect/${r.id}`"
                  color="neutral"
                  variant="soft"
                  size="xs"
                  icon="i-lucide-bar-chart-2"
                  title="View Analytics"
                />

                <UButton
                  :color="r.expired ? 'success' : 'warning'"
                  variant="soft"
                  size="xs"
                  @click="toggleLinkStatus(r)"
                >
                  {{ r.expired ? 'Enable' : 'Disable' }}
                </UButton>

                <UButton
                  color="error"
                  variant="soft"
                  size="xs"
                  icon="i-lucide-trash-2"
                  @click="handleDeleteLink(r.id)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
