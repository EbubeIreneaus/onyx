<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: ['auth'] })

const route = useRoute()
const config = useRuntimeConfig()
const { fetchDomainById, deleteDomain } = useDomains()
const router = useRouter()

const domainId = computed(() => Number(route.params.id))
const domain = ref<DomainOut | null>(null)
const loading = ref(true)

const defaultDomain = config.public.domainName || 'onyx.com'

onMounted(async () => {
  if (isNaN(domainId.value)) {
    router.push('/dashboard/domains')
    return
  }
  domain.value = await fetchDomainById(domainId.value)
  loading.value = false
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function handleDelete() {
  if (!domain.value) return
  await deleteDomain(domain.value.id)
  router.push('/dashboard/domains')
}

useSeoMeta({ title: computed(() => domain.value ? `${domain.value.name} — Verification` : 'Domain Details') })
</script>

<template>
  <div>
    <!-- Back button -->
    <div class="mb-6">
      <UButton
        to="/dashboard/domains"
        icon="i-lucide-arrow-left"
        color="neutral"
        variant="ghost"
        size="sm"
      >
        Back to Domains
      </UButton>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="py-16 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-zinc-500" />
    </div>

    <!-- Not found -->
    <div v-else-if="!domain" class="py-16 text-center">
      <p class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Domain not found</p>
      <p class="text-sm text-slate-500 mb-4">The requested domain does not exist or you do not have permission to view it.</p>
      <UButton to="/dashboard/domains">Return to Domains</UButton>
    </div>

    <!-- Domain Content -->
    <div v-else class="max-w-3xl space-y-6">
      <!-- Domain Header Card -->
      <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3 mb-1">
            <h1 class="text-xl font-bold text-slate-900 dark:text-white">{{ domain.name }}</h1>
            <UBadge
              :color="domain.txt_verified && domain.cname_verified ? 'success' : 'warning'"
              variant="soft"
              size="sm"
            >
              {{ domain.txt_verified && domain.cname_verified ? 'Fully Verified' : 'Pending Verification' }}
            </UBadge>
          </div>
          <p class="text-xs text-slate-400">Added on {{ formatDate(domain.created_at) }}</p>
        </div>

        <UButton
          icon="i-lucide-trash-2"
          color="error"
          variant="soft"
          size="sm"
          @click="handleDelete"
        >
          Delete Domain
        </UButton>
      </div>

      <!-- Banner 1: TXT Record Verification -->
      <div
        class="p-6 rounded-2xl border transition-all space-y-4"
        :class="domain.txt_verified
          ? 'bg-emerald-50/70 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40 text-emerald-900 dark:text-emerald-200'
          : 'bg-rose-50/70 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800/40 text-rose-900 dark:text-rose-200'"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <UIcon
              :name="domain.txt_verified ? 'i-lucide-check-circle-2' : 'i-lucide-alert-octagon'"
              class="w-6 h-6 shrink-0 mt-0.5"
              :class="domain.txt_verified ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'"
            />
            <div>
              <h2 class="text-base font-semibold">1. TXT Record Verification</h2>
              <p class="text-xs mt-1 leading-relaxed opacity-90">
                {{ domain.txt_verified
                  ? 'TXT record is verified! Domain ownership confirmed.'
                  : 'Add the following TXT record to your domain\'s DNS settings to verify domain ownership.' }}
              </p>
            </div>
          </div>

          <UBadge
            :color="domain.txt_verified ? 'success' : 'error'"
            variant="solid"
            size="sm"
          >
            {{ domain.txt_verified ? 'Verified' : 'Unverified' }}
          </UBadge>
        </div>

        <!-- DNS Record Instructions Table -->
        <div class="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/60 dark:border-slate-800/60 space-y-2.5 font-mono text-xs text-slate-800 dark:text-slate-200">
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Type</span>
            <span class="font-semibold">TXT</span>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Host / Name</span>
            <span class="font-semibold">@ (or {{ domain.name }})</span>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Value / Token</span>
            <span class="select-all font-semibold break-all text-zinc-900 dark:text-zinc-100">
              {{ domain.txt_token || 'onyx-domain-verification=pending' }}
            </span>
          </div>
        </div>

        <!-- Action button -->
        <div class="flex justify-end pt-1">
          <UButton
            color="neutral"
            size="sm"
            :disabled="domain.txt_verified || true"
          >
            {{ domain.txt_verified ? 'TXT Record Verified' : 'Verify TXT Record' }}
          </UButton>
        </div>
      </div>

      <!-- Banner 2: CNAME Record Instructions -->
      <div
        class="p-6 rounded-2xl border transition-all space-y-4"
        :class="domain.cname_verified
          ? 'bg-emerald-50/70 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40 text-emerald-900 dark:text-emerald-200'
          : 'bg-rose-50/70 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800/40 text-rose-900 dark:text-rose-200'"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <UIcon
              :name="domain.cname_verified ? 'i-lucide-check-circle-2' : 'i-lucide-alert-octagon'"
              class="w-6 h-6 shrink-0 mt-0.5"
              :class="domain.cname_verified ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'"
            />
            <div>
              <h2 class="text-base font-semibold">2. CNAME Destination Record</h2>
              <p class="text-xs mt-1 leading-relaxed opacity-90">
                {{ domain.cname_verified
                  ? 'CNAME record is pointing to Onyx successfully!'
                  : 'Point your domain to Onyx servers so traffic can be routed to your short links.' }}
              </p>
            </div>
          </div>

          <UBadge
            :color="domain.cname_verified ? 'success' : 'error'"
            variant="solid"
            size="sm"
          >
            {{ domain.cname_verified ? 'Verified' : 'Unverified' }}
          </UBadge>
        </div>

        <!-- CNAME Instruction Table -->
        <div class="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/60 dark:border-slate-800/60 space-y-2.5 font-mono text-xs text-slate-800 dark:text-slate-200">
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Type</span>
            <span class="font-semibold">CNAME</span>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Host / Name</span>
            <span class="font-semibold">@ (or subdomain)</span>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
            <span class="w-20 text-slate-400 font-sans font-medium uppercase text-[10px] tracking-wider">Target Value</span>
            <span class="select-all font-semibold break-all text-zinc-900 dark:text-zinc-100">
              https://{{ defaultDomain }}
            </span>
          </div>
        </div>

        <!-- Action button -->
        <div class="flex justify-end pt-1">
          <UButton
            color="neutral"
            size="sm"
            :disabled="domain.cname_verified || true"
          >
            {{ domain.cname_verified ? 'CNAME Record Verified' : 'Verify CNAME Record' }}
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>
