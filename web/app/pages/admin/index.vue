<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

useSeoMeta({
  title: 'Admin Overview — Onyx'
})

const api = useApi()
const loading = ref(true)

interface AdminAnalytics {
  total_users: number
  active_users: number
  suspended_users: number
  total_redirects: number
  total_visits: number
  total_domains: number
  verified_domains: number
  active_tiers_count: number
}

const stats = ref<AdminAnalytics | null>(null)

const fetchStats = async () => {
  loading.value = true
  try {
    stats.value = await api<AdminAnalytics>('/api/v1/admin/analytics')
  } catch (err: any) {
    // ignore
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-12">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-extrabold text-white flex items-center gap-2.5">
          <UIcon
            name="i-lucide-shield-check"
            class="w-7 h-7 text-rose-500"
          />
          Admin Control Center
        </h1>
        <p class="text-sm text-zinc-400 mt-1">
          Platform health, system metrics, and administrative moderation controls.
        </p>
      </div>

      <UButton
        icon="i-lucide-refresh-cw"
        color="neutral"
        variant="soft"
        size="sm"
        :loading="loading"
        @click="fetchStats"
      >
        Refresh Metrics
      </UButton>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="py-16 flex justify-center"
    >
      <UIcon
        name="i-lucide-loader-2"
        class="w-8 h-8 animate-spin text-zinc-500"
      />
    </div>

    <template v-else-if="stats">
      <!-- Top Metrics Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Users Card -->
        <NuxtLink
          to="/admin/users"
          class="p-5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-2xl space-y-3 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Total Users</span>
            <div class="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <UIcon
                name="i-lucide-users"
                class="w-5 h-5"
              />
            </div>
          </div>
          <div class="text-3xl font-extrabold text-white font-mono">{{ stats.total_users }}</div>
          <div class="flex items-center justify-between text-xs text-zinc-400 pt-1">
            <span>Active: <strong class="text-emerald-400 font-mono">{{ stats.active_users }}</strong></span>
            <span>Suspended: <strong class="text-rose-400 font-mono">{{ stats.suspended_users }}</strong></span>
          </div>
        </NuxtLink>

        <!-- Redirects Card -->
        <NuxtLink
          to="/admin/links"
          class="p-5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-2xl space-y-3 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Short Links</span>
            <div class="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <UIcon
                name="i-lucide-link"
                class="w-5 h-5"
              />
            </div>
          </div>
          <div class="text-3xl font-extrabold text-white font-mono">{{ stats.total_redirects }}</div>
          <p class="text-xs text-zinc-400">Platform-wide created redirects</p>
        </NuxtLink>

        <!-- Clicks Card -->
        <div class="p-5 bg-zinc-900 border border-zinc-800 rounded-2xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Total Visits</span>
            <div class="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <UIcon
                name="i-lucide-mouse-pointer-click"
                class="w-5 h-5"
              />
            </div>
          </div>
          <div class="text-3xl font-extrabold text-white font-mono">
            {{ stats.total_visits }}
          </div>
          <p class="text-xs text-zinc-400">
            Resolved visitor redirections
          </p>
        </div>

        <!-- Domains Card -->
        <NuxtLink
          to="/admin/domains"
          class="p-5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-2xl space-y-3 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Custom Domains</span>
            <div class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <UIcon
                name="i-lucide-globe"
                class="w-5 h-5"
              />
            </div>
          </div>
          <div class="text-3xl font-extrabold text-white font-mono">{{ stats.total_domains }}</div>
          <p class="text-xs text-zinc-400">Verified: <strong class="text-emerald-400 font-mono">{{ stats.verified_domains }}</strong></p>
        </NuxtLink>
      </div>

      <!-- Quick Action Directory -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-white flex items-center gap-2">
          <UIcon
            name="i-lucide-sliders"
            class="w-5 h-5 text-rose-400"
          />
          Administrative Tools
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NuxtLink
            to="/admin/users"
            class="p-6 bg-zinc-900/60 border border-zinc-800 hover:border-rose-500/50 rounded-2xl space-y-2 group transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-white group-hover:text-rose-400 transition-colors flex items-center gap-2">
                <UIcon
                  name="i-lucide-users"
                  class="w-5 h-5 text-emerald-400"
                />
                User Management
              </span>
              <UIcon
                name="i-lucide-arrow-right"
                class="w-4 h-4 text-zinc-500 group-hover:text-rose-400"
              />
            </div>
            <p class="text-xs text-zinc-400">Search users, suspend/reinstate accounts, update roles, and manage user tier subscriptions.</p>
          </NuxtLink>

          <NuxtLink
            to="/admin/domains"
            class="p-6 bg-zinc-900/60 border border-zinc-800 hover:border-rose-500/50 rounded-2xl space-y-2 group transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-white group-hover:text-rose-400 transition-colors flex items-center gap-2">
                <UIcon
                  name="i-lucide-globe"
                  class="w-5 h-5 text-cyan-400"
                />
                Domain Verification & Force-Verify
              </span>
              <UIcon
                name="i-lucide-arrow-right"
                class="w-4 h-4 text-zinc-500 group-hover:text-rose-400"
              />
            </div>
            <p class="text-xs text-zinc-400">Global domain directory. Manually force-verify TXT/CNAME records without waiting for DNS propagation.</p>
          </NuxtLink>

          <NuxtLink
            to="/admin/links"
            class="p-6 bg-zinc-900/60 border border-zinc-800 hover:border-rose-500/50 rounded-2xl space-y-2 group transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-white group-hover:text-rose-400 transition-colors flex items-center gap-2">
                <UIcon
                  name="i-lucide-link"
                  class="w-5 h-5 text-indigo-400"
                />
                Short Link Moderation
              </span>
              <UIcon
                name="i-lucide-arrow-right"
                class="w-4 h-4 text-zinc-500 group-hover:text-rose-400"
              />
            </div>
            <p class="text-xs text-zinc-400">Global short link directory. Search destination URLs, disable suspicious links, and delete records.</p>
          </NuxtLink>

          <NuxtLink
            to="/admin/tiers"
            class="p-6 bg-zinc-900/60 border border-zinc-800 hover:border-rose-500/50 rounded-2xl space-y-2 group transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-white group-hover:text-rose-400 transition-colors flex items-center gap-2">
                <UIcon
                  name="i-lucide-layers"
                  class="w-5 h-5 text-amber-400"
                />
                Subscription Tiers & Paystack
              </span>
              <UIcon
                name="i-lucide-arrow-right"
                class="w-4 h-4 text-zinc-500 group-hover:text-rose-400"
              />
            </div>
            <p class="text-xs text-zinc-400">Configure tier pricing, quotas (`api:access`, `custom:domain`, link durability), and sync with Paystack.</p>
          </NuxtLink>
        </div>
      </div>
    </template>
  </div>
</template>
