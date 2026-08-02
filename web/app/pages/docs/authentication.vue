<script setup lang="ts">
definePageMeta({
  layout: 'docs',
})

useSeoMeta({
  title: 'Authentication — Onyx API Docs',
})

const config = useRuntimeConfig()
const baseApiUrl = computed(() => config.public.apiBase || 'http://localhost:8000')
</script>

<template>
  <div class="space-y-8">
    <div>
      <div class="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
        <UIcon name="i-lucide-key" class="w-4 h-4" />
        Security
      </div>
      <h1 class="text-3xl font-extrabold text-white">Authentication</h1>
      <p class="text-zinc-400 mt-2 text-base leading-relaxed">
        The Onyx API uses API Secret Tokens to authenticate requests. Users with Developer API Access (<code class="text-emerald-400 font-mono">api:access</code>) can generate and manage lifetime tokens in the Developer Dashboard.
      </p>
    </div>

    <!-- Header Authorization Methods -->
    <div class="space-y-4">
      <h2 class="text-xl font-bold text-white">Authentication Headers</h2>
      <p class="text-sm text-zinc-400">
        You can pass your API secret key in either the <code class="text-emerald-400 font-mono">Authorization</code> header or the <code class="text-emerald-400 font-mono">X-API-Key</code> header with every request.
      </p>

      <div class="space-y-3">
        <!-- Option 1 -->
        <div class="p-4 bg-zinc-900 border border-zinc-800 rounded-xl space-y-1">
          <div class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Option 1: Bearer Token</div>
          <div class="font-mono text-sm text-emerald-400">
            Authorization: Bearer onyx_sec_YOUR_API_TOKEN
          </div>
        </div>

        <!-- Option 2 -->
        <div class="p-4 bg-zinc-900 border border-zinc-800 rounded-xl space-y-1">
          <div class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Option 2: X-API-Key Header</div>
          <div class="font-mono text-sm text-emerald-400">
            X-API-Key: onyx_sec_YOUR_API_TOKEN
          </div>
        </div>
      </div>
    </div>

    <!-- HTTP Status Code Responses -->
    <div class="space-y-4 pt-4 border-t border-zinc-800">
      <h2 class="text-xl font-bold text-white">Authentication Error Responses</h2>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-zinc-300">
          <thead class="bg-zinc-900 text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
            <tr>
              <th class="py-3 px-4">Status Code</th>
              <th class="py-3 px-4">Error Message</th>
              <th class="py-3 px-4">Description</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60 font-mono">
            <tr>
              <td class="py-3 px-4 text-rose-400 font-bold">401 Unauthorized</td>
              <td class="py-3 px-4">Missing authentication token or API key</td>
              <td class="py-3 px-4 text-zinc-400 font-sans">No Authorization or X-API-Key header was included.</td>
            </tr>
            <tr>
              <td class="py-3 px-4 text-rose-400 font-bold">401 Unauthorized</td>
              <td class="py-3 px-4">Invalid API key provided</td>
              <td class="py-3 px-4 text-zinc-400 font-sans">The API key passed is invalid or has been revoked.</td>
            </tr>
            <tr>
              <td class="py-3 px-4 text-amber-400 font-bold">403 Forbidden</td>
              <td class="py-3 px-4">API access is not enabled on your tier...</td>
              <td class="py-3 px-4 text-zinc-400 font-sans">Your subscription plan does not include <code class="text-emerald-400">api:access</code>.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
