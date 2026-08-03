<script setup lang="ts">
definePageMeta({
  layout: 'docs'
})

useSeoMeta({
  title: 'Redirects & Short Links API — Onyx API Docs'
})

const config = useRuntimeConfig()
const baseApiUrl = computed(() => config.public.apiBase || 'http://localhost:8000')
</script>

<template>
  <div class="space-y-10">
    <div>
      <div class="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
        <UIcon
          name="i-lucide-link"
          class="w-4 h-4"
        />
        Endpoints
      </div>
      <h1 class="text-3xl font-extrabold text-white">
        Redirects & Short Links API
      </h1>
      <p class="text-zinc-400 mt-2 text-base leading-relaxed">
        Create branded short links, list links, query real-time analytics, resolve destinations for incoming visitors, and update link targets.
      </p>
    </div>

    <!-- 1. Create Short Link Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">POST</span>
        <code class="text-sm font-mono text-white">/api/v1/client/create-short</code>
      </div>
      <p class="text-xs text-zinc-400">
        Creates a short link under the default domain or a verified custom domain.
      </p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Request Body (JSON)
        </h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono overflow-x-auto max-w-full block">{
  "destination": "https://example.com/long-page-target",
  "domain": "onyx.com", // Optional: verified custom domain or default domain
  "slug": "promo2026"   // Optional: custom slug (cleaned automatically)
}</pre>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Expected Response (200 OK)
        </h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono overflow-x-auto max-w-full block">{
  "id": "7a9f8b2c-1234-5678-90ab-cdef12345678",
  "destination": "https://example.com/long-page-target",
  "domain": "onyx.com",
  "slug": "promo2026",
  "visits": 0,
  "created_at": "2026-08-02T18:30:00Z",
  "expired": false,
  "expired_on": "2026-08-16T18:30:00Z"
}</pre>
      </div>
    </div>

    <!-- 2. Get Link Analytics Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 font-mono text-xs font-bold border border-blue-500/20">GET</span>
        <code class="text-sm font-mono text-white">/api/v1/client/redirects/{redirect_id}/analytics</code>
      </div>
      <p class="text-xs text-zinc-400">
        Retrieves detailed click charts, geolocation by country, device breakdown, and visitor logs.
      </p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Query Parameters
        </h4>
        <ul class="text-xs text-zinc-400 space-y-1 font-mono">
          <li><code class="text-emerald-400">period</code> (optional): <span class="text-zinc-300">"daily"</span> (default), <span class="text-zinc-300">"weekly"</span>, or <span class="text-zinc-300">"yearly"</span></li>
        </ul>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Expected Response (200 OK)
        </h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono overflow-x-auto max-w-full block">{
  "redirect_id": "7a9f8b2c-1234-5678-90ab-cdef12345678",
  "domain": "onyx.com",
  "slug": "promo2026",
  "destination": "https://example.com/long-page-target",
  "total_clicks": 142,
  "period": "daily",
  "chart": [
    {"label": "00:00", "clicks": 12},
    {"label": "04:00", "clicks": 35}
  ],
  "countries": [
    {"country": "United States", "clicks": 85, "percentage": 59.8},
    {"country": "Nigeria", "clicks": 30, "percentage": 21.1}
  ],
  "devices": [
    {"device": "Chrome on Windows (Desktop)", "clicks": 90, "percentage": 63.3}
  ]
}</pre>
      </div>
    </div>

    <!-- 3. Public Resolve Redirect Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">POST</span>
        <code class="text-sm font-mono text-white">/api/v1/client/resolve-redirect</code>
      </div>
      <p class="text-xs text-zinc-400">
        Public resolution endpoint called when visitors load short link pages. Uses Redis caching and enqueues background visitor tracking.
      </p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Request Body (JSON)
        </h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono overflow-x-auto max-w-full block">{
  "domain": "onyx.com",
  "slug": "promo2026",
  "full_url": "https://onyx.com/promo2026"
}</pre>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Expected Response (200 OK)
        </h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono">{
  "found": true,
  "destination": "https://example.com/long-page-target",
  "expired": false
}</pre>
      </div>
    </div>
  </div>
</template>
