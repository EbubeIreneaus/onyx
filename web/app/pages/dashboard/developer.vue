<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: ['auth']
})

useSeoMeta({
  title: 'Developer API — Onyx'
})

const config = useRuntimeConfig()
const toast = useToast()
const { apiKeyData, loading, generating, fetchApiKey, generateApiKey, rotateApiKey, revokeApiKey } = useApiKey()

const showKey = ref(false)
const showRotateModal = ref(false)

const defaultApiBase = computed(() => config.public.apiBase || 'http://localhost:8000')

onMounted(() => {
  fetchApiKey()
})

const copyToClipboard = async (text: string) => {
  await navigator.clipboard.writeText(text)
  toast.add({ title: 'Copied to clipboard!', color: 'success', duration: 2000 })
}

const handleGenerate = async () => {
  await generateApiKey()
}

const handleRotate = async () => {
  await rotateApiKey()
  showRotateModal.value = false
}

const handleRevoke = async () => {
  await revokeApiKey()
}

const curlExample = computed(() => {
  const token = apiKeyData.value?.api_key || 'onyx_sec_YOUR_API_TOKEN'
  return `curl -X POST "${defaultApiBase.value}/api/v1/client/create-short" \\
  -H "Authorization: Bearer ${token}" \\
  -H "Content-Type: application/json" \\
  -d '{"destination": "https://example.com/long-page", "slug": "my-promo"}'`
})

const pythonExample = computed(() => {
  const token = apiKeyData.value?.api_key || 'onyx_sec_YOUR_API_TOKEN'
  return `import requests

url = "${defaultApiBase.value}/api/v1/client/create-short"
headers = {
    "Authorization": "Bearer ${token}",
    "Content-Type": "application/json"
}
payload = {
    "destination": "https://example.com/long-page",
    "slug": "my-promo"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())`
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
          <UIcon
            name="i-lucide-code-2"
            class="w-7 h-7 text-emerald-500"
          />
          Developer API Keys
        </h1>
        <p class="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
          Generate lifetime API secret tokens to integrate short links and domain verification directly into your applications.
        </p>
      </div>

      <UButton
        to="/docs/get-started"
        icon="i-lucide-book-open"
        color="neutral"
        variant="soft"
        size="md"
      >
        View API Documentation
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

    <template v-else>
      <!-- Upgrade Required Banner if user does NOT have api:access -->
      <div
        v-if="!apiKeyData?.has_api_access"
        class="p-6 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-500/20 rounded-2xl space-y-4"
      >
        <div class="flex items-start gap-4">
          <div class="p-3 bg-amber-500/10 text-amber-400 rounded-xl shrink-0">
            <UIcon
              name="i-lucide-lock"
              class="w-6 h-6"
            />
          </div>
          <div class="space-y-1">
            <h2 class="text-base font-bold text-slate-900 dark:text-white">
              Developer API Access Disabled
            </h2>
            <p class="text-sm text-zinc-400 leading-relaxed">
              API token generation is exclusive to plans with Developer API Access (<code class="text-amber-400 font-mono">api:access</code>). Upgrade your subscription to unlock automated link creation, custom domain management, and webhooks.
            </p>
          </div>
        </div>

        <div class="pt-2 flex items-center gap-3">
          <!-- Disabled Generate Button with Tooltip -->
          <UTooltip text="Upgrade account to unlock Developer API Access">
            <UButton
              disabled
              icon="i-lucide-key"
              color="neutral"
              variant="solid"
              size="md"
              class="cursor-not-allowed opacity-60"
            >
              Generate API Token
            </UButton>
          </UTooltip>

          <UButton
            to="/dashboard/subscriptions"
            color="warning"
            variant="solid"
            size="md"
          >
            Upgrade Subscription Plan
          </UButton>
        </div>
      </div>

      <!-- Main API Key Card (for users WITH api:access) -->
      <div
        v-else
        class="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-xs space-y-6"
      >
        <div class="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <UIcon
                name="i-lucide-key-round"
                class="w-5 h-5 text-emerald-400"
              />
              Active API Token
            </h2>
            <p class="text-xs text-zinc-500">
              Lifetime authentication secret token for programmatically accessing Onyx endpoints.
            </p>
          </div>

          <UBadge
            :color="apiKeyData?.api_key ? 'success' : 'neutral'"
            variant="soft"
            size="xs"
            :label="apiKeyData?.api_key ? 'Active' : 'No Key Generated'"
          />
        </div>

        <!-- No Key Generated Yet -->
        <div
          v-if="!apiKeyData?.api_key"
          class="py-8 text-center space-y-4"
        >
          <div class="inline-flex p-4 rounded-full bg-zinc-800 text-zinc-400">
            <UIcon
              name="i-lucide-key"
              class="w-8 h-8"
            />
          </div>
          <p class="text-sm text-zinc-400">
            You haven't generated an API token yet.
          </p>
          <UButton
            icon="i-lucide-sparkles"
            color="success"
            variant="solid"
            size="md"
            :loading="generating"
            @click="handleGenerate"
          >
            Generate API Token
          </UButton>
        </div>

        <!-- API Key Display Box -->
        <div
          v-else
          class="space-y-4"
        >
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div class="flex-1 flex items-center gap-3 p-3.5 bg-zinc-950 rounded-xl border border-zinc-800 font-mono text-sm">
              <UIcon
                name="i-lucide-shield-check"
                class="w-4 h-4 text-emerald-400 shrink-0"
              />
              <span class="truncate text-zinc-200">
                {{ showKey ? apiKeyData.api_key : `${apiKeyData.api_key?.slice(0, 12)}••••••••••••••••••••••••` }}
              </span>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <UButton
                :icon="showKey ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                color="neutral"
                variant="soft"
                size="md"
                title="Toggle Visibility"
                @click="showKey = !showKey"
              />
              <UButton
                icon="i-lucide-copy"
                color="neutral"
                variant="soft"
                size="md"
                title="Copy Token"
                @click="copyToClipboard(apiKeyData.api_key || '')"
              >
                Copy
              </UButton>
              <UButton
                icon="i-lucide-refresh-cw"
                color="warning"
                variant="soft"
                size="md"
                title="Rotate Key"
                @click="showRotateModal = true"
              >
                Rotate Token
              </UButton>
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-4 text-xs text-zinc-500 pt-2">
            <div class="flex items-center gap-1.5">
              <UIcon
                name="i-lucide-clock"
                class="w-3.5 h-3.5 text-zinc-400"
              />
              Created: <span class="text-zinc-300 font-medium">{{ apiKeyData.created_at ? new Date(apiKeyData.created_at).toLocaleDateString() : 'N/A' }}</span>
            </div>
            <div class="text-zinc-400">
              Expiration: <span class="text-emerald-400 font-medium">Lifetime (Until Rotated)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quickstart Integration Snippets -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <UIcon
            name="i-lucide-terminal"
            class="w-5 h-5 text-indigo-400"
          />
          Quickstart Integration
        </h2>

        <div class="grid grid-cols-1 gap-4">
          <!-- cURL Tab -->
          <div class="p-5 bg-zinc-900 rounded-2xl border border-zinc-800 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">cURL Command</span>
              <UButton
                icon="i-lucide-copy"
                size="xs"
                color="neutral"
                variant="ghost"
                @click="copyToClipboard(curlExample)"
              >
                Copy
              </UButton>
            </div>
            <pre class="p-4 bg-zinc-950 rounded-xl text-xs text-emerald-400 font-mono overflow-x-auto leading-relaxed">{{ curlExample }}</pre>
          </div>

          <!-- Python Tab -->
          <div class="p-5 bg-zinc-900 rounded-2xl border border-zinc-800 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Python (Requests)</span>
              <UButton
                icon="i-lucide-copy"
                size="xs"
                color="neutral"
                variant="ghost"
                @click="copyToClipboard(pythonExample)"
              >
                Copy
              </UButton>
            </div>
            <pre class="p-4 bg-zinc-950 rounded-xl text-xs text-emerald-400 font-mono overflow-x-auto leading-relaxed">{{ pythonExample }}</pre>
          </div>
        </div>
      </div>
    </template>

    <!-- Rotate Token Confirmation Modal -->
    <UModal
      v-model:open="showRotateModal"
      title="Rotate API Token"
    >
      <template #body>
        <div class="space-y-4 p-1">
          <UAlert
            description="Rotating your API token will immediately revoke the current key. Any external apps or scripts using the old key will stop working until updated."
            color="warning"
            variant="soft"
            icon="i-lucide-alert-triangle"
          />
          <p class="text-sm text-zinc-300">
            Are you sure you want to generate a new secret API token?
          </p>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-3 w-full">
          <UButton
            color="neutral"
            variant="soft"
            @click="showRotateModal = false"
          >
            Cancel
          </UButton>
          <UButton
            color="warning"
            :loading="generating"
            @click="handleRotate"
          >
            Rotate Key Now
          </UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
