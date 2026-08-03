<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: ['auth'] })

useSeoMeta({ title: 'Dashboard — Onyx' })

const { user } = useAuth()
const { links, activeLinks, totalClicks, fetchLinks, pending, createLink, copyLink, deleteLink } = useLinks()
const { domains, fetchDomains } = useDomains()

fetchLinks()
fetchDomains()

const stats = computed(() => [
  {
    label: 'Active Links',
    value: activeLinks.value.length,
    icon: 'i-lucide-link',
    color: 'text-zinc-600 dark:text-zinc-400',
    bg: 'bg-zinc-50 dark:bg-zinc-950/50',
    change: `+${activeLinks.value.length > 0 ? activeLinks.value.length : 0}`,
    positive: true
  },
  {
    label: 'Total Clicks',
    value: totalClicks.value.toLocaleString(),
    icon: 'i-lucide-mouse-pointer-click',
    color: 'text-indigo-600 dark:text-indigo-400',
    bg: 'bg-indigo-50 dark:bg-indigo-950/50',
    change: null,
    positive: true
  },
  {
    label: 'Domains',
    value: domains.value.length,
    icon: 'i-lucide-globe',
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-950/50',
    change: null,
    positive: true
  },
  {
    label: 'Subscription',
    value: user.value?.current_subscription?.tier?.name || 'Free',
    icon: 'i-lucide-zap',
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-50 dark:bg-amber-950/50',
    change: null,
    positive: true
  }
])

// Quick create
const showCreate = ref(false)
const newUrl = ref('')
const creating = ref(false)

async function quickCreate() {
  if (!newUrl.value.trim()) return
  creating.value = true
  await createLink({ destination: newUrl.value.trim() })
  creating.value = false
  newUrl.value = ''
  showCreate.value = false
}

// Format date nicely
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'short', year: 'numeric' })
}

function truncate(s: string, n = 40) {
  return s.length > n ? s.slice(0, n) + '…' : s
}

const recentLinks = computed(() => [...links.value].slice(0, 8))
</script>

<template>
  <div>
    <!-- Welcome banner -->
    <div class="mb-8 p-6 rounded-md bg-zinc-900 dark:bg-zinc-950 text-white relative overflow-hidden border border-zinc-800">
      <div class="relative z-10">
        <p class="text-zinc-400 text-sm mb-1">
          Good day 👋
        </p>
        <h1 class="text-2xl font-bold mb-4 text-zinc-100">
          {{ user?.fullname }}
        </h1>
        <div class="flex flex-wrap gap-3">
          <UButton
            color="neutral"
            size="sm"
            class="rounded-md"
            icon="i-lucide-plus"
            @click="showCreate = !showCreate"
          >
            Create link
          </UButton>
          <NuxtLink to="/dashboard/links">
            <UButton
              color="neutral"
              variant="ghost"
              size="sm"
              class="rounded-md text-white border-zinc-700 hover:bg-zinc-800"
              trailing-icon="i-lucide-arrow-right"
            >
              View all links
            </UButton>
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Create Link Modal -->
    <CreateLinkModal
      v-model:open="showCreate"
      @created="fetchLinks"
    />

    <!-- Stats grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="p-5 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors"
      >
        <div class="flex items-start justify-between mb-4">
          <div
            class="inline-flex p-2.5 rounded-md"
            :class="stat.bg"
          >
            <UIcon
              :name="stat.icon"
              class="w-5 h-5"
              :class="stat.color"
            />
          </div>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mb-1">
          {{ stat.value }}
        </p>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          {{ stat.label }}
        </p>
      </div>
    </div>

    <!-- Recent links -->
    <div class="bg-white dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800">
      <div class="flex items-center justify-between p-5 border-b border-zinc-200 dark:border-zinc-800">
        <h3 class="font-semibold text-slate-900 dark:text-white">
          Recent Links
        </h3>
        <NuxtLink to="/dashboard/links">
          <UButton
            size="xs"
            color="neutral"
            variant="ghost"
            trailing-icon="i-lucide-arrow-right"
          >
            View all
          </UButton>
        </NuxtLink>
      </div>

      <!-- Loading -->
      <div
        v-if="pending"
        class="p-8 flex justify-center"
      >
        <UIcon
          name="i-lucide-loader-2"
          class="w-6 h-6 animate-spin text-zinc-500"
        />
      </div>

      <!-- Empty -->
      <div
        v-else-if="!recentLinks.length"
        class="p-12 text-center"
      >
        <div class="inline-flex p-4 rounded-md bg-zinc-50 dark:bg-zinc-950/40 mb-4">
          <UIcon
            name="i-lucide-link"
            class="w-8 h-8 text-zinc-500"
          />
        </div>
        <p class="text-slate-900 dark:text-white font-semibold mb-1">
          No links yet
        </p>
        <p class="text-slate-500 text-sm mb-4">
          Create your first short link to get started.
        </p>
        <UButton
          size="sm"
          icon="i-lucide-plus"
          @click="showCreate = true"
        >
          Create link
        </UButton>
      </div>

      <!-- Table -->
      <div
        v-else
        class="divide-y divide-slate-100 dark:divide-slate-800"
      >
        <div
          v-for="link in recentLinks"
          :key="link.redirect_id"
          class="flex items-center gap-4 px-5 py-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
        >
          <!-- Link icon -->
          <div class="shrink-0 w-9 h-9 rounded-xl bg-zinc-50 dark:bg-zinc-950/40 flex items-center justify-center">
            <UIcon
              name="i-lucide-link-2"
              class="w-4 h-4 text-zinc-600 dark:text-zinc-400"
            />
          </div>

          <!-- Link info -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
              {{ link.domain }}/{{ link.slug }}
            </p>
            <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
              {{ truncate(link.destination) }}
            </p>
          </div>

          <!-- Stats -->
          <div class="hidden sm:flex items-center gap-4 shrink-0">
            <div class="text-center">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">
                {{ link.visitor_count || 0 }}
              </p>
              <p class="text-xs text-slate-400">
                clicks
              </p>
            </div>
            <div class="text-center">
              <p class="text-xs text-slate-400">
                {{ formatDate(link.created_at) }}
              </p>
            </div>
          </div>

          <!-- Status badge -->
          <UBadge
            :color="link.expired ? 'neutral' : 'success'"
            variant="soft"
            size="sm"
            :label="link.expired ? 'Expired' : 'Active'"
            class="shrink-0"
          />

          <!-- Actions (appear on hover) -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
            <UButton
              icon="i-lucide-copy"
              size="xs"
              color="neutral"
              variant="ghost"
              @click="copyLink(link)"
            />
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              @click="deleteLink(link.redirect_id)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
