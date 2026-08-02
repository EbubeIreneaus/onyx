<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useSeoMeta({
  title: 'Manage Users — Admin',
})

const api = useApi()
const toast = useToast()

interface AdminUser {
  id: number
  user_id: string
  fullname: string
  email: string
  is_admin: boolean
  status: string
  tier_name: string
  created_at: string
  redirects_count: number
  domains_count: number
}

const users = ref<AdminUser[]>([])
const loading = ref(true)
const searchQuery = ref('')

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = searchQuery.value ? `?search=${encodeURIComponent(searchQuery.value)}` : ''
    users.value = await api<AdminUser[]>(`/api/v1/admin/users${params}`)
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: 'Failed to load users list', color: 'error' })
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})

const toggleUserStatus = async (user: AdminUser) => {
  const nextStatus = user.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
  try {
    await api(`/api/v1/admin/users/${user.user_id}/status`, {
      method: 'PATCH',
      body: { status: nextStatus },
    })
    user.status = nextStatus
    toast.add({ title: `User ${nextStatus.toLowerCase()} successfully`, color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to update status', color: 'error' })
  }
}

const toggleAdminRole = async (user: AdminUser) => {
  const nextAdmin = !user.is_admin
  try {
    await api(`/api/v1/admin/users/${user.user_id}/role`, {
      method: 'PATCH',
      body: { is_admin: nextAdmin },
    })
    user.is_admin = nextAdmin
    toast.add({ title: `User admin status updated to ${nextAdmin}`, color: 'success' })
  }
  catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to update role', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-6 pb-12">
    <!-- Header & Search -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-white flex items-center gap-2">
          <UIcon name="i-lucide-users" class="w-6 h-6 text-emerald-400" />
          User Management
        </h1>
        <p class="text-xs text-zinc-400 mt-1">View, suspend, elevate roles, and inspect user activity.</p>
      </div>

      <div class="flex items-center gap-3">
        <UInput
          v-model="searchQuery"
          icon="i-lucide-search"
          placeholder="Search by email or name..."
          class="w-64"
          @keyup.enter="fetchUsers"
        />
        <UButton color="neutral" variant="soft" icon="i-lucide-rotate-cw" @click="fetchUsers" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Users Table -->
    <div v-else class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-zinc-300">
          <thead class="bg-zinc-950 text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
            <tr>
              <th class="py-3.5 px-4">User Details</th>
              <th class="py-3.5 px-4">Subscription Tier</th>
              <th class="py-3.5 px-4">Role</th>
              <th class="py-3.5 px-4">Status</th>
              <th class="py-3.5 px-4">Stats</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60">
            <tr v-for="u in users" :key="u.id" class="hover:bg-zinc-800/30 transition-colors">
              <!-- Name & Email -->
              <td class="py-4 px-4">
                <div class="flex items-center gap-3">
                  <UAvatar :alt="u.fullname" size="sm" class="bg-zinc-800 text-zinc-200 shrink-0" />
                  <div class="min-w-0">
                    <p class="font-bold text-white truncate">{{ u.fullname }}</p>
                    <p class="text-zinc-400 text-[11px] font-mono truncate">{{ u.email }}</p>
                  </div>
                </div>
              </td>

              <!-- Tier -->
              <td class="py-4 px-4">
                <UBadge color="info" variant="soft" size="xs" :label="u.tier_name" />
              </td>

              <!-- Role -->
              <td class="py-4 px-4">
                <UBadge
                  :color="u.is_admin ? 'warning' : 'neutral'"
                  variant="soft"
                  size="xs"
                  :label="u.is_admin ? 'Admin' : 'User'"
                />
              </td>

              <!-- Status -->
              <td class="py-4 px-4">
                <UBadge
                  :color="u.status === 'ACTIVE' ? 'success' : 'error'"
                  variant="soft"
                  size="xs"
                  :label="u.status"
                />
              </td>

              <!-- Stats -->
              <td class="py-4 px-4 text-zinc-400 font-mono">
                <div>Links: <strong class="text-white">{{ u.redirects_count }}</strong></div>
                <div>Domains: <strong class="text-white">{{ u.domains_count }}</strong></div>
              </td>

              <!-- Actions -->
              <td class="py-4 px-4 text-right space-x-2">
                <UButton
                  :color="u.status === 'ACTIVE' ? 'error' : 'success'"
                  variant="soft"
                  size="xs"
                  @click="toggleUserStatus(u)"
                >
                  {{ u.status === 'ACTIVE' ? 'Suspend' : 'Reinstate' }}
                </UButton>

                <UButton
                  :color="u.is_admin ? 'neutral' : 'warning'"
                  variant="soft"
                  size="xs"
                  @click="toggleAdminRole(u)"
                >
                  {{ u.is_admin ? 'Revoke Admin' : 'Make Admin' }}
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
