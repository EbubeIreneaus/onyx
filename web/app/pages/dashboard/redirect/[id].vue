<script setup lang="ts">
import type { RedirectAnalyticsResponse } from '~/composables/useLinks'

definePageMeta({
  layout: 'dashboard',
})

const route = useRoute()
const redirectId = computed(() => route.params.id as string)

const { fetchAnalytics, copyLink, deleteLink } = useLinks()

const loading = ref(true)
const period = ref<'daily' | 'weekly' | 'yearly'>('daily')
const data = ref<RedirectAnalyticsResponse | null>(null)

const periods = [
  { label: 'Daily (7 Days)', value: 'daily' },
  { label: 'Weekly (12 Weeks)', value: 'weekly' },
  { label: 'Yearly (12 Months)', value: 'yearly' },
]

const loadAnalytics = async () => {
  loading.value = true
  try {
    data.value = await fetchAnalytics(redirectId.value, period.value)
  }
  finally {
    loading.value = false
  }
}

const setPeriod = (p: 'daily' | 'weekly' | 'yearly') => {
  period.value = p
  loadAnalytics()
}

// Compute max visits for scaling chart heights
const maxChartVisits = computed(() => {
  if (!data.value?.chart_data?.length) return 1
  const max = Math.max(...data.value.chart_data.map(d => d.visits))
  return max > 0 ? max : 1
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatShortDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadAnalytics()
})
</script>

<template>
  <div class="space-y-6 max-w-6xl mx-auto pb-12">
    <!-- Top Bar Navigation -->
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <UButton
          to="/dashboard/links"
          icon="i-lucide-arrow-left"
          color="neutral"
          variant="ghost"
          size="sm"
        >
          Back to Links
        </UButton>
        <span class="text-zinc-600 dark:text-zinc-400">/</span>
        <h1 class="text-lg font-bold text-slate-900 dark:text-white truncate">
          Link Analytics
        </h1>
      </div>

      <!-- Period Tabs -->
      <div class="flex items-center bg-zinc-100 dark:bg-zinc-800/80 p-1 rounded-lg border border-zinc-200 dark:border-zinc-700/50">
        <button
          v-for="item in periods"
          :key="item.value"
          class="px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-150"
          :class="period === item.value 
            ? 'bg-white dark:bg-zinc-900 text-slate-900 dark:text-white shadow-xs font-semibold' 
            : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'"
          @click="setPeriod(item.value as any)"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-24 flex justify-center items-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Error State -->
    <div v-else-if="!data" class="py-16 text-center space-y-4 bg-zinc-900/50 rounded-2xl border border-zinc-800">
      <UIcon name="i-lucide-alert-circle" class="w-10 h-10 text-rose-400 mx-auto" />
      <p class="text-base text-zinc-300 font-medium">Unable to load analytics for this link.</p>
      <UButton to="/dashboard/links" color="neutral" variant="soft">Return to Links</UButton>
    </div>

    <template v-else>
      <!-- Link Overview Card -->
      <div class="p-6 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2.5">
              <a
                :href="`https://${data.domain}/${data.slug}`"
                target="_blank"
                class="text-xl font-bold text-slate-900 dark:text-white hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
              >
                {{ data.domain }}/{{ data.slug }}
              </a>
              <UBadge
                :color="data.expired ? 'neutral' : 'success'"
                variant="soft"
                size="xs"
                :label="data.expired ? 'Expired' : 'Active'"
              />
            </div>
            <p class="text-sm text-zinc-500 dark:text-zinc-400 truncate max-w-xl">
              Destination: <a :href="data.destination" target="_blank" class="underline hover:text-zinc-300">{{ data.destination }}</a>
            </p>
          </div>

          <!-- Quick Actions -->
          <div class="flex items-center gap-2">
            <UButton
              icon="i-lucide-copy"
              color="neutral"
              variant="outline"
              size="sm"
              @click="copyLink(data as any)"
            >
              Copy Link
            </UButton>
            <UButton
              :to="`https://${data.domain}/${data.slug}`"
              target="_blank"
              icon="i-lucide-external-link"
              color="neutral"
              variant="soft"
              size="sm"
            >
              Visit
            </UButton>
          </div>
        </div>

        <div class="pt-3 border-t border-zinc-100 dark:border-zinc-800/80 flex flex-wrap gap-6 text-xs text-zinc-500">
          <div>Created: <span class="font-medium text-zinc-300">{{ formatDate(data.created_at) }}</span></div>
          <div v-if="data.expired_on">Expires: <span class="font-medium text-zinc-300">{{ formatDate(data.expired_on) }}</span></div>
          <div>Link ID: <span class="font-mono text-zinc-400">{{ data.redirect_id }}</span></div>
        </div>
      </div>

      <!-- Stat Cards Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Total Clicks -->
        <div class="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-1">
          <div class="flex items-center justify-between text-zinc-500">
            <span class="text-xs font-medium uppercase tracking-wider">Total Clicks</span>
            <UIcon name="i-lucide-mouse-pointer-click" class="w-4 h-4 text-emerald-400" />
          </div>
          <p class="text-2xl font-extrabold text-slate-900 dark:text-white">
            {{ data.total_clicks.toLocaleString() }}
          </p>
          <p class="text-xs text-zinc-500">Total clicks in {{ period }} period</p>
        </div>

        <!-- Unique Visitors -->
        <div class="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-1">
          <div class="flex items-center justify-between text-zinc-500">
            <span class="text-xs font-medium uppercase tracking-wider">Unique Visitors</span>
            <UIcon name="i-lucide-users" class="w-4 h-4 text-indigo-400" />
          </div>
          <p class="text-2xl font-extrabold text-slate-900 dark:text-white">
            {{ data.unique_visitors.toLocaleString() }}
          </p>
          <p class="text-xs text-zinc-500">Distinct visitor IPs</p>
        </div>

        <!-- Top Country -->
        <div class="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-1">
          <div class="flex items-center justify-between text-zinc-500">
            <span class="text-xs font-medium uppercase tracking-wider">Top Location</span>
            <UIcon name="i-lucide-globe" class="w-4 h-4 text-cyan-400" />
          </div>
          <p class="text-xl font-extrabold text-slate-900 dark:text-white truncate">
            {{ data.top_country || 'None' }}
          </p>
          <p class="text-xs text-zinc-500">Most active country/region</p>
        </div>

        <!-- Top Device -->
        <div class="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-1">
          <div class="flex items-center justify-between text-zinc-500">
            <span class="text-xs font-medium uppercase tracking-wider">Top Device</span>
            <UIcon name="i-lucide-smartphone" class="w-4 h-4 text-purple-400" />
          </div>
          <p class="text-xl font-extrabold text-slate-900 dark:text-white truncate">
            {{ data.top_device || 'None' }}
          </p>
          <p class="text-xs text-zinc-500">Primary visitor platform</p>
        </div>
      </div>

      <!-- Time Series Chart -->
      <div class="p-6 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-base font-bold text-slate-900 dark:text-white">Click Traffic Over Time</h2>
            <p class="text-xs text-zinc-500">Visits grouped by {{ period }} intervals</p>
          </div>
          <UBadge color="neutral" variant="outline" size="xs">
            {{ data.chart_data.length }} Data Points
          </UBadge>
        </div>

        <!-- Chart Visualization -->
        <div class="h-56 flex items-end gap-3 pt-6 pb-2 border-b border-zinc-200 dark:border-zinc-800">
          <div
            v-for="(point, idx) in data.chart_data"
            :key="idx"
            class="flex-1 flex flex-col items-center gap-2 h-full justify-end group relative"
          >
            <!-- Hover Tooltip -->
            <div class="absolute -top-10 opacity-0 group-hover:opacity-100 transition-all duration-150 pointer-events-none z-10 bg-zinc-800 text-white text-xs py-1 px-2.5 rounded-md shadow-lg font-mono whitespace-nowrap">
              {{ point.date }}: {{ point.visits }} clicks
            </div>

            <!-- Bar -->
            <div
              class="w-full max-w-[40px] rounded-t-md bg-gradient-to-t from-emerald-600 to-emerald-400 group-hover:from-emerald-500 group-hover:to-emerald-300 transition-all duration-300"
              :style="{ height: `${Math.max((point.visits / maxChartVisits) * 100, 6)}%` }"
            />

            <!-- Label -->
            <span class="text-[10px] font-medium text-zinc-500 truncate w-full text-center">
              {{ point.date }}
            </span>
          </div>
        </div>
      </div>

      <!-- Two-Column Breakdown: Countries & Devices -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Countries Breakdown -->
        <div class="p-6 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-lucide-map-pin" class="w-4 h-4 text-emerald-400" />
              Location Breakdown
            </h2>
            <span class="text-xs text-zinc-500">{{ data.country_data.length }} Countries</span>
          </div>

          <div v-if="!data.country_data.length" class="py-8 text-center text-xs text-zinc-500">
            No geographic data collected yet.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="item in data.country_data"
              :key="item.country"
              class="space-y-1.5"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-medium text-zinc-300 flex items-center gap-2">
                  <UIcon name="i-lucide-globe" class="w-3.5 h-3.5 text-zinc-500" />
                  {{ item.country }}
                </span>
                <span class="text-zinc-400 font-mono">
                  {{ item.visits }} visits ({{ item.percentage }}%)
                </span>
              </div>
              <!-- Progress Bar -->
              <div class="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                <div
                  class="bg-emerald-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${item.percentage}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Device Breakdown -->
        <div class="p-6 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-lucide-laptop" class="w-4 h-4 text-indigo-400" />
              Devices & Browsers
            </h2>
            <span class="text-xs text-zinc-500">{{ data.device_data.length }} Platforms</span>
          </div>

          <div v-if="!data.device_data.length" class="py-8 text-center text-xs text-zinc-500">
            No device details logged yet.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="item in data.device_data"
              :key="item.device"
              class="flex items-center justify-between p-3 bg-zinc-950/50 rounded-lg border border-zinc-800/60 text-xs"
            >
              <span class="font-medium text-zinc-300 truncate max-w-[70%]">
                {{ item.device }}
              </span>
              <span class="font-mono text-emerald-400 font-semibold">
                {{ item.visits }} visits
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Visitor Logs Table -->
      <div class="p-6 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-base font-bold text-slate-900 dark:text-white">Recent Visitors Log</h2>
            <p class="text-xs text-zinc-500">Latest 20 clicks recorded for this link</p>
          </div>
        </div>

        <div v-if="!data.recent_visitors.length" class="py-8 text-center text-xs text-zinc-500">
          No visitors recorded yet. Share your short link to start tracking!
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs text-zinc-300">
            <thead class="bg-zinc-950/60 text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
              <tr>
                <th class="py-3 px-4">IP Address</th>
                <th class="py-3 px-4">Location</th>
                <th class="py-3 px-4">Device & Browser</th>
                <th class="py-3 px-4">Date & Time</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/60">
              <tr
                v-for="visitor in data.recent_visitors"
                :key="visitor.id"
                class="hover:bg-zinc-800/30 transition-colors"
              >
                <td class="py-3 px-4 font-mono text-zinc-400">{{ visitor.ip }}</td>
                <td class="py-3 px-4">
                  <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300 text-[11px]">
                    <UIcon name="i-lucide-map-pin" class="w-3 h-3 text-emerald-400" />
                    {{ visitor.location || 'Unknown' }}
                  </span>
                </td>
                <td class="py-3 px-4 truncate max-w-xs">{{ visitor.device || 'Unknown' }}</td>
                <td class="py-3 px-4 text-zinc-500">{{ formatShortDate(visitor.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
