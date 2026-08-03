<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const config = useRuntimeConfig()

const loading = ref(true)
const expired = ref(false)
const errorMsg = ref<string | null>(null)

const slug = computed(() => {
  const parts = route.params.slug
  if (Array.isArray(parts)) {
    return parts.join('/')
  }
  return parts || ''
})

onMounted(async () => {
  const fullUrl = window.location.href
  const domain = window.location.host

  try {
    const res = await $fetch<{
      found: boolean
      destination?: string
      expired?: boolean
      message?: string
    }>('/api/v1/client/resolve-redirect', {
      method: 'POST',
      baseURL: config.public.apiBase || 'http://localhost:8000',
      body: {
        domain,
        slug: slug.value,
        full_url: fullUrl
      }
    })

    if (res.found && res.destination) {
      window.location.replace(res.destination)
      return
    }

    if (res.expired) {
      expired.value = true
    }
    errorMsg.value = res.message || 'Link not found or has been deactivated.'
    loading.value = false
  } catch (err: any) {
    errorMsg.value = 'Failed to resolve link destination.'
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-zinc-950 text-white p-6 font-sans">
    <!-- Redirecting loader -->
    <div
      v-if="loading"
      class="text-center space-y-4"
    >
      <AppLogo />
      <div class="flex items-center justify-center gap-2 text-sm text-zinc-400">
        <UIcon
          name="i-lucide-loader-2"
          class="w-4 h-4 animate-spin text-zinc-400"
        />
        <span>Redirecting you to destination...</span>
      </div>
    </div>

    <!-- Link Expired or Not Found -->
    <div
      v-else
      class="max-w-md w-full text-center space-y-6 bg-zinc-900 border border-zinc-800 p-8 rounded-2xl shadow-xl"
    >
      <div
        class="inline-flex p-4 rounded-full"
        :class="expired ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'"
      >
        <UIcon
          :name="expired ? 'i-lucide-clock' : 'i-lucide-link-2-off'"
          class="w-10 h-10"
        />
      </div>

      <div>
        <h1 class="text-xl font-bold text-white mb-2">
          {{ expired ? 'Link Expired' : 'Link Not Found' }}
        </h1>
        <p class="text-sm text-zinc-400 leading-relaxed">
          {{ errorMsg }}
        </p>
      </div>

      <div class="pt-2">
        <UButton
          to="/"
          color="neutral"
          variant="soft"
          size="md"
        >
          Return to Homepage
        </UButton>
      </div>
    </div>
  </div>
</template>
