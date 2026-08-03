<script setup lang="ts">
definePageMeta({
  layout: 'docs'
})

useSeoMeta({
  title: 'Getting Started — Onyx API Docs'
})

const config = useRuntimeConfig()
const baseApiUrl = computed(() => config.public.apiBase || 'http://localhost:8000')
</script>

<template>
  <div class="space-y-8">
    <div>
      <div class="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
        <UIcon
          name="i-lucide-rocket"
          class="w-4 h-4"
        />
        Overview
      </div>
      <h1 class="text-3xl font-extrabold text-white">
        Getting Started
      </h1>
      <p class="text-zinc-400 mt-2 text-base leading-relaxed">
        Welcome to the Onyx Developer REST API. Our API allows you to programmatically register custom domains, verify DNS records, create branded short links, and retrieve real-time click & visitor analytics.
      </p>
    </div>

    <!-- Base URL Box -->
    <div class="p-5 bg-zinc-900 border border-zinc-800 rounded-xl space-y-2">
      <h3 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
        Base API Endpoint
      </h3>
      <div class="p-3 bg-zinc-950 rounded-lg font-mono text-sm text-emerald-400 border border-zinc-800">
        {{ baseApiUrl }}/api/v1/client
      </div>
      <p class="text-xs text-zinc-500">
        All client requests must be made over HTTPS in production.
      </p>
    </div>

    <!-- Main Features / Summary of Important Routes -->
    <div class="space-y-4 pt-4 border-t border-zinc-800">
      <h2 class="text-xl font-bold text-white">
        Core API Modules
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Authentication -->
        <NuxtLink
          to="/docs/authentication"
          class="p-5 bg-zinc-900/60 border border-zinc-800 hover:border-emerald-500/50 rounded-xl space-y-2 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-white group-hover:text-emerald-400 transition-colors">Authentication</span>
            <UIcon
              name="i-lucide-arrow-right"
              class="w-4 h-4 text-zinc-500 group-hover:text-emerald-400"
            />
          </div>
          <p class="text-xs text-zinc-400">Authenticate requests using lifetime secret API keys (`X-API-Key` or `Authorization: Bearer`).</p>
        </NuxtLink>

        <!-- Domains -->
        <NuxtLink
          to="/docs/domains"
          class="p-5 bg-zinc-900/60 border border-zinc-800 hover:border-emerald-500/50 rounded-xl space-y-2 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-white group-hover:text-emerald-400 transition-colors">Domains API</span>
            <UIcon
              name="i-lucide-arrow-right"
              class="w-4 h-4 text-zinc-500 group-hover:text-emerald-400"
            />
          </div>
          <p class="text-xs text-zinc-400">Register custom apex domains and subdomains, trigger authoritative DNS verification.</p>
        </NuxtLink>

        <!-- Redirects -->
        <NuxtLink
          to="/docs/redirects"
          class="p-5 bg-zinc-900/60 border border-zinc-800 hover:border-emerald-500/50 rounded-xl space-y-2 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-white group-hover:text-emerald-400 transition-colors">Short Links API</span>
            <UIcon
              name="i-lucide-arrow-right"
              class="w-4 h-4 text-zinc-500 group-hover:text-emerald-400"
            />
          </div>
          <p class="text-xs text-zinc-400">Create, list, update, and delete short links with custom slugs and expiration dates.</p>
        </NuxtLink>

        <!-- Analytics -->
        <NuxtLink
          to="/docs/redirects"
          class="p-5 bg-zinc-900/60 border border-zinc-800 hover:border-emerald-500/50 rounded-xl space-y-2 group transition-all"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-white group-hover:text-emerald-400 transition-colors">Analytics & Geolocation</span>
            <UIcon
              name="i-lucide-arrow-right"
              class="w-4 h-4 text-zinc-500 group-hover:text-emerald-400"
            />
          </div>
          <p class="text-xs text-zinc-400">Retrieve click time-series, country breakdowns, device platforms, and visitor logs.</p>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
