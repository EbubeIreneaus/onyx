<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: ['auth'] })

useSeoMeta({ title: 'Links — Onyx' })

const { links, activeLinks, expiredLinks, totalClicks, fetchLinks, pending, createLink, copyLink, deleteLink } = useLinks()

fetchLinks()

const showModal = ref(false)
const qrModalOpen = ref(false)
const selectedQrLink = ref<RedirectOut | null>(null)
let qrPollTimer: ReturnType<typeof setInterval> | null = null

function getQrState(value: RedirectOut['qr_image']) {
  if (!value || value === '') return 'none'
  if (value === 'generating') return 'generating'
  return 'ready'
}

function startQrPolling() {
  if (qrPollTimer) return
  qrPollTimer = setInterval(() => {
    if (!pending.value && links.value.some(link => getQrState(link.qr_image) === 'generating')) {
      fetchLinks()
    }
  }, 4000)
}

function stopQrPolling() {
  if (qrPollTimer) {
    clearInterval(qrPollTimer)
    qrPollTimer = null
  }
}

function openQrModal(link: RedirectOut) {
  selectedQrLink.value = link
  if (getQrState(link.qr_image) === 'generating') {
    fetchLinks()
  }
  qrModalOpen.value = true
}

function downloadQr(link: RedirectOut) {
  if (!link.qr_image) return
  const anchor = document.createElement('a')
  anchor.href = link.qr_image
  anchor.download = `qr-${link.slug || link.redirect_id}.png`
  anchor.click()
}

// Search + filter
const search = ref('')
const filter = ref<'all' | 'active' | 'expired'>('all')

const filteredLinks = computed(() => {
  let list = filter.value === 'active'
    ? activeLinks.value
    : filter.value === 'expired'
      ? expiredLinks.value
      : links.value

  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(l =>
      l.slug?.toLowerCase().includes(q)
      || l.destination.toLowerCase().includes(q)
      || l.domain.toLowerCase().includes(q)
    )
  }
  return list
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'short', year: 'numeric' })
}
function truncate(s: string, n = 45) {
  return s.length > n ? s.slice(0, n) + '…' : s
}

onMounted(() => {
  startQrPolling()
})

onBeforeUnmount(() => {
  stopQrPolling()
})
</script>

<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div class="flex items-center gap-2 flex-wrap">
        <UBadge
          v-for="tab in [
            { key: 'all', label: `All (${links.length})` },
            { key: 'active', label: `Active (${activeLinks.length})` },
            { key: 'expired', label: `Expired (${expiredLinks.length})` },
          ]"
          :key="tab.key"
          :color="filter === tab.key ? 'primary' : 'neutral'"
          :variant="filter === tab.key ? 'solid' : 'soft'"
          class="cursor-pointer px-3 py-1.5 text-sm font-medium rounded-lg"
          @click="filter = tab.key as any"
        >
          {{ tab.label }}
        </UBadge>
      </div>

      <div class="flex items-center gap-2 w-full sm:w-auto">
        <UInput
          v-model="search"
          placeholder="Search links..."
          icon="i-lucide-search"
          size="sm"
          class="flex-1 sm:w-64"
        />
        <UButton size="sm" icon="i-lucide-plus" class="shrink-0" @click="showModal = true">
          New link
        </UButton>
      </div>
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div class="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ links.length }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Total links</p>
      </div>
      <div class="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
        <p class="text-2xl font-bold text-zinc-600 dark:text-zinc-400">{{ activeLinks.length }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Active</p>
      </div>
      <div class="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center">
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ totalClicks.toLocaleString() }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Total clicks</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="py-16 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Empty state -->
    <div v-else-if="!filteredLinks.length" class="py-16 text-center">
      <div class="inline-flex p-5 rounded-2xl bg-zinc-50 dark:bg-zinc-950/40 mb-4">
        <UIcon name="i-lucide-link" class="w-10 h-10 text-zinc-500" />
      </div>
      <p class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
        {{ search ? 'No links match your search' : 'No links here yet' }}
      </p>
      <p class="text-slate-500 text-sm mb-5">
        {{ search ? 'Try a different keyword.' : 'Create your first short link to get started.' }}
      </p>
      <UButton v-if="!search" icon="i-lucide-plus" @click="showModal = true">Create link</UButton>
    </div>

    <!-- Links list -->
    <div v-else class="space-y-2">
      <div
        v-for="link in filteredLinks"
        :key="link.redirect_id"
        class="flex items-center gap-4 p-4 bg-white dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-200 group"
      >
        <!-- Favicon-like icon -->
        <div class="shrink-0 w-10 h-10 rounded-md bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center">
          <UIcon
            :name="link.expired ? 'i-lucide-link-2-off' : 'i-lucide-link-2'"
            class="w-5 h-5"
            :class="link.expired ? 'text-slate-400' : 'text-zinc-600 dark:text-zinc-400'"
          />
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <NuxtLink
              :to="`/dashboard/redirect/${link.redirect_id}`"
              class="text-sm font-semibold text-slate-900 dark:text-white hover:text-zinc-600 dark:hover:text-zinc-400 transition-colors"
            >
              {{ link.domain }}/{{ link.slug }}
            </NuxtLink>
            <UBadge
              :color="link.expired ? 'neutral' : 'success'"
              variant="soft"
              size="xs"
              :label="link.expired ? 'Expired' : 'Active'"
            />
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 truncate">{{ truncate(link.destination) }}</p>
        </div>

        <!-- Metadata (hidden on mobile) -->
        <div class="hidden md:flex items-center gap-6 shrink-0 text-center">
          <NuxtLink :to="`/dashboard/redirect/${link.redirect_id}`" class="hover:underline">
            <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ (link.visitor_count || 0).toLocaleString() }}</p>
            <p class="text-xs text-slate-400">clicks</p>
          </NuxtLink>
          <div>
            <p class="text-xs text-slate-500">{{ formatDate(link.created_at) }}</p>
            <p class="text-xs text-slate-400">created</p>
          </div>
          <div v-if="link.expired_on">
            <p class="text-xs text-slate-500">{{ formatDate(link.expired_on) }}</p>
            <p class="text-xs text-slate-400">expires</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 shrink-0">
          <UButton icon="i-lucide-bar-chart-3" size="xs" color="neutral" variant="ghost" title="View Analytics" :to="`/dashboard/redirect/${link.redirect_id}`" />
          <UButton icon="i-lucide-copy" size="xs" color="neutral" variant="ghost" title="Copy link" @click="copyLink(link)" />
          <UButton
            v-if="getQrState(link.qr_image) !== 'none'"
            :icon="getQrState(link.qr_image) === 'generating' ? 'i-lucide-clock-3' : 'i-lucide-qr-code'"
            size="xs"
            color="neutral"
            variant="ghost"
            :title="getQrState(link.qr_image) === 'generating' ? 'QR image is generating' : 'View QR code'"
            :disabled="getQrState(link.qr_image) === 'generating'"
            @click="getQrState(link.qr_image) === 'ready' ? openQrModal(link) : null"
          />
          <UButton icon="i-lucide-external-link" size="xs" color="neutral" variant="ghost" title="Open link"
            :to="`https://${link.domain}/${link.slug}`" target="_blank" />
          <UButton icon="i-lucide-trash-2" size="xs" color="error" variant="ghost" title="Delete link" @click="deleteLink(link.redirect_id)" />
        </div>
      </div>
    </div>

    <!-- Create Link Modal -->
    <CreateLinkModal v-model:open="showModal" @created="fetchLinks" />

    <div
      v-if="qrModalOpen && selectedQrLink"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
      @click.self="qrModalOpen = false"
    >
      <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-zinc-900">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">QR Code</h3>
          <div class="flex items-center gap-2">
            <UButton v-if="getQrState(selectedQrLink.qr_image) === 'ready'" icon="i-lucide-download" size="sm" @click="downloadQr(selectedQrLink)">
              Download
            </UButton>
            <UButton icon="i-lucide-x" size="sm" color="neutral" variant="ghost" @click="qrModalOpen = false" />
          </div>
        </div>
        <div v-if="getQrState(selectedQrLink.qr_image) === 'ready'" class="flex justify-center">
          <img :src="selectedQrLink.qr_image" alt="QR Code" class="max-w-full max-h-[60vh] rounded-lg border border-zinc-200 dark:border-zinc-800" />
        </div>
        <p v-else-if="getQrState(selectedQrLink.qr_image) === 'generating'" class="text-sm text-slate-500">
          Your image is generating.
        </p>
        <p v-else class="text-sm text-slate-500">QR image is not available yet.</p>
      </div>
    </div>
  </div>
</template>
