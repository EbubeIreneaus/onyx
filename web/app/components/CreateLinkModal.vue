<script setup lang="ts">
const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'created'): void
}>()

const { user } = useAuth()
const { createLink, creating } = useLinks()
const { checkDomain } = useDomains()
const config = useRuntimeConfig()

const defaultDomain = (config.public.domainName as string) || 'onyx.com'

// Form state
const destination = ref('')
const slug = ref('')
const linkType = ref<'free' | 'subdomain' | 'custom'>('free')
const subdomainPrefix = ref('')
const customDomainInput = ref('')

// Check state
const checkingDomain = ref(false)
const domainStatus = ref<{
  available: boolean
  registered: boolean
  owned_by_user: boolean
  txt_verified: boolean
  domain_id: number | null
  message: string
} | null>(null)

// Permissions derived from user tier
const permissions = computed<string[]>(() => {
  return [...(user.value?.current_subscription?.tier?.permissions || [])]
})

const hasFreeLink = computed(() => permissions.value.includes('free:link') || permissions.value.includes('app:free_link'))
const hasCustomPath = computed(() => permissions.value.includes('custom:path') || permissions.value.includes('app:custom_path'))
const hasSubdomain = computed(() => permissions.value.includes('onyx:subdomain') || permissions.value.includes('app:onyx_subdomain'))
const hasCustomDomain = computed(() => permissions.value.includes('custom:domain') || permissions.value.includes('app:custom_domain'))

// Target full domain name based on selection
const effectiveDomain = computed<string>(() => {
  if (linkType.value === 'free') {
    return defaultDomain
  }
  if (linkType.value === 'subdomain') {
    const prefix = subdomainPrefix.value.trim().toLowerCase()
    return prefix ? `${prefix}.${defaultDomain}` : ''
  }
  return customDomainInput.value.trim().toLowerCase()
})

// Debounced live domain checker
let checkTimer: any = null
watch([effectiveDomain, slug], () => {
  domainStatus.value = null
  if (linkType.value === 'free') {
    checkingDomain.value = false
    return
  }

  if (!effectiveDomain.value) {
    checkingDomain.value = false
    return
  }

  checkingDomain.value = true
  clearTimeout(checkTimer)
  checkTimer = setTimeout(async () => {
    const res = await checkDomain(effectiveDomain.value, slug.value || undefined)
    checkingDomain.value = false
    if (res) {
      domainStatus.value = {
        available: res.available,
        registered: res.registered,
        owned_by_user: res.owned_by_user,
        txt_verified: res.txt_verified,
        domain_id: res.domain_id,
        message: res.message,
      }
    }
  }, 400)
})

// Reset form when modal closes or opens
watch(() => props.open, (val) => {
  if (val) {
    destination.value = ''
    slug.value = ''
    linkType.value = 'free'
    subdomainPrefix.value = ''
    customDomainInput.value = ''
    domainStatus.value = null
    checkingDomain.value = false
  }
})

const canSubmit = computed(() => {
  if (!destination.value.trim()) return false
  if (creating.value || checkingDomain.value) return false
  if (linkType.value !== 'free') {
    if (!effectiveDomain.value) return false
    if (!domainStatus.value?.available) return false
  }
  return true
})

async function handleSubmit() {
  if (!canSubmit.value) return

  const payload = {
    destination: destination.value.trim(),
    domain: effectiveDomain.value,
    slug: hasCustomPath.value && slug.value.trim() ? slug.value.trim() : undefined,
    type: linkType.value,
  }

  const result = await createLink(payload)
  if (result) {
    emit('update:open', false)
    emit('created')
  }
}
</script>

<template>
  <UModal
    :open="open"
    title="Create New Short Link"
    description="Shorten long URLs with custom aliases and custom domain support."
    @update:open="emit('update:open', $event)"
  >
    <template #body>
      <form class="space-y-5 p-1" @submit.prevent="handleSubmit">
        <!-- Destination URL -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Destination URL <span class="text-rose-500">*</span>
          </label>
          <UInput
            v-model="destination"
            placeholder="https://example.com/long-page-url"
            icon="i-lucide-link"
            size="md"
            class="w-full"
            required
          />
        </div>

        <!-- Alias / Custom Path -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Alias / Custom Path
            </label>
            <span v-if="!hasCustomPath" class="text-xs text-amber-600 dark:text-amber-400 font-medium">
              Requires Custom Path permission
            </span>
          </div>
          <UInput
            v-model="slug"
            placeholder="my-custom-slug"
            icon="i-lucide-hash"
            size="md"
            class="w-full"
            :disabled="!hasCustomPath"
          />
        </div>

        <!-- Domain Type Radio Buttons (Row Layout) -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Link Type & Domain
          </label>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 p-1.5 bg-slate-100 dark:bg-slate-800/60 rounded-xl">
            <!-- Free Radio -->
            <label
              class="flex items-center gap-2 p-2.5 rounded-lg border text-xs font-medium cursor-pointer transition-all"
              :class="linkType === 'free' ? 'bg-white dark:bg-slate-900 border-zinc-300 dark:border-zinc-700 shadow-xs text-slate-900 dark:text-white' : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'"
            >
              <input
                v-model="linkType"
                type="radio"
                value="free"
                class="accent-zinc-900 dark:accent-zinc-100"
              >
              <span>Free ({{ defaultDomain }})</span>
            </label>

            <!-- Onyx Subdomain Radio -->
            <label
              class="flex items-center gap-2 p-2.5 rounded-lg border text-xs font-medium transition-all"
              :class="[
                !hasSubdomain ? 'opacity-50 cursor-not-allowed border-transparent text-slate-400' : 'cursor-pointer',
                linkType === 'subdomain' ? 'bg-white dark:bg-slate-900 border-zinc-300 dark:border-zinc-700 shadow-xs text-slate-900 dark:text-white' : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              ]"
            >
              <input
                v-model="linkType"
                type="radio"
                value="subdomain"
                :disabled="!hasSubdomain"
                class="accent-zinc-900 dark:accent-zinc-100"
              >
              <span>Onyx Subdomain</span>
            </label>

            <!-- Custom Domain Radio -->
            <label
              class="flex items-center gap-2 p-2.5 rounded-lg border text-xs font-medium transition-all"
              :class="[
                !hasCustomDomain ? 'opacity-50 cursor-not-allowed border-transparent text-slate-400' : 'cursor-pointer',
                linkType === 'custom' ? 'bg-white dark:bg-slate-900 border-zinc-300 dark:border-zinc-700 shadow-xs text-slate-900 dark:text-white' : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              ]"
            >
              <input
                v-model="linkType"
                type="radio"
                value="custom"
                :disabled="!hasCustomDomain"
                class="accent-zinc-900 dark:accent-zinc-100"
              >
              <span>Custom Domain</span>
            </label>
          </div>
        </div>

        <!-- Onyx Subdomain Input -->
        <div v-if="linkType === 'subdomain'" class="space-y-2">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Subdomain Prefix
          </label>
          <div class="flex items-center">
            <UInput
              v-model="subdomainPrefix"
              placeholder="mybrand"
              size="md"
              class="flex-1 rounded-r-none"
            />
            <span class="h-10 px-3 flex items-center bg-slate-100 dark:bg-slate-800 border border-l-0 border-slate-200 dark:border-slate-700 rounded-r-lg text-xs font-mono text-slate-500">
              .{{ defaultDomain }}
            </span>
          </div>
        </div>

        <!-- Custom Domain Input -->
        <div v-if="linkType === 'custom'" class="space-y-2">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Custom Domain
          </label>
          <div class="relative">
            <UInput
              v-model="customDomainInput"
              placeholder="links.mybrand.com"
              icon="i-lucide-globe"
              size="md"
              class="w-full"
            />
            <div v-if="checkingDomain" class="absolute right-3 top-2.5">
              <UIcon name="i-lucide-loader-2" class="w-5 h-5 animate-spin text-zinc-500" />
            </div>
          </div>
        </div>

        <!-- Domain Availability / Error Feedback Banners -->
        <div v-if="linkType !== 'free' && effectiveDomain">
          <!-- Checking indicator -->
          <p v-if="checkingDomain" class="text-xs text-slate-400 flex items-center gap-1.5">
            <UIcon name="i-lucide-loader-2" class="w-3.5 h-3.5 animate-spin" />
            Checking domain availability...
          </p>

          <!-- Domain not registered -->
          <div
            v-else-if="domainStatus && !domainStatus.registered"
            class="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/50 text-xs text-amber-800 dark:text-amber-300 space-y-1.5"
          >
            <div class="flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-alert-triangle" class="w-4 h-4 text-amber-600 shrink-0" />
              <span>Domain not found</span>
            </div>
            <p class="text-amber-700 dark:text-amber-400 leading-relaxed">
              This domain is not registered in your Onyx account. Please add it first in the domains settings.
            </p>
            <NuxtLink
              to="/dashboard/domains"
              class="inline-flex items-center gap-1 text-xs font-semibold text-amber-900 dark:text-amber-200 hover:underline mt-1"
              @click="emit('update:open', false)"
            >
              <span>Go to Custom Domains</span>
              <UIcon name="i-lucide-arrow-right" class="w-3 h-3" />
            </NuxtLink>
          </div>

          <!-- Domain registered by another user -->
          <div
            v-else-if="domainStatus && domainStatus.registered && !domainStatus.owned_by_user"
            class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 text-xs text-rose-800 dark:text-rose-300"
          >
            <div class="flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-x-circle" class="w-4 h-4 text-rose-600 shrink-0" />
              <span>Domain is already in use by another user</span>
            </div>
          </div>

          <!-- Domain registered by current user but NOT verified -->
          <div
            v-else-if="domainStatus && domainStatus.registered && domainStatus.owned_by_user && !domainStatus.txt_verified"
            class="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/50 text-xs text-amber-800 dark:text-amber-300 space-y-1.5"
          >
            <div class="flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-shield-alert" class="w-4 h-4 text-amber-600 shrink-0" />
              <span>Domain DNS TXT record is not verified</span>
            </div>
            <p class="text-amber-700 dark:text-amber-400">
              Complete DNS verification for {{ effectiveDomain }} before creating short links.
            </p>
            <NuxtLink
              :to="`/dashboard/domains/${domainStatus.domain_id}`"
              class="inline-flex items-center gap-1 text-xs font-semibold text-amber-900 dark:text-amber-200 hover:underline mt-1"
              @click="emit('update:open', false)"
            >
              <span>View Verification Instructions</span>
              <UIcon name="i-lucide-arrow-right" class="w-3 h-3" />
            </NuxtLink>
          </div>

          <!-- Domain verified & available -->
          <div
            v-else-if="domainStatus && domainStatus.available"
            class="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2"
          >
            <UIcon name="i-lucide-check-circle-2" class="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Domain is verified and ready to use!</span>
          </div>

          <!-- Domain slug clash -->
          <div
            v-else-if="domainStatus && !domainStatus.available && domainStatus.message"
            class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 text-xs text-rose-800 dark:text-rose-300 flex items-center gap-2"
          >
            <UIcon name="i-lucide-alert-circle" class="w-4 h-4 text-rose-600 shrink-0" />
            <span>{{ domainStatus.message }}</span>
          </div>
        </div>
      </form>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="neutral" variant="ghost" @click="emit('update:open', false)">
          Cancel
        </UButton>
        <UButton
          color="primary"
          size="md"
          :loading="creating"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          Create Short Link
        </UButton>
      </div>
    </template>
  </UModal>
</template>
