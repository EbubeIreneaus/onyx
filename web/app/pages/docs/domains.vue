<script setup lang="ts">
definePageMeta({
  layout: 'docs',
})

useSeoMeta({
  title: 'Domains API — Onyx API Docs',
})

const config = useRuntimeConfig()
const baseApiUrl = computed(() => config.public.apiBase || 'http://localhost:8000')
</script>

<template>
  <div class="space-y-10">
    <div>
      <div class="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
        <UIcon name="i-lucide-globe" class="w-4 h-4" />
        Endpoints
      </div>
      <h1 class="text-3xl font-extrabold text-white">Domains API</h1>
      <p class="text-zinc-400 mt-2 text-base leading-relaxed">
        Manage custom apex domains and subdomains. Add new domains, list existing domains, trigger DNS verification against root authoritative nameservers, and delete domain records.
      </p>
    </div>

    <!-- 1. Add Domain Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">POST</span>
        <code class="text-sm font-mono text-white">/api/v1/client/create-domain</code>
      </div>
      <p class="text-xs text-zinc-400">Registers a custom root domain or subdomain under the user's account.</p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Request Body (JSON)</h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono">{
  "name": "brand.com" // or "links.brand.com"
}</pre>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Expected Response (201 Created)</h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono">{
  "id": 12,
  "name": "brand.com",
  "txt_token": "onyx-verify-3a9f8b2...",
  "txt_verified": false,
  "cname_verified": false,
  "is_root_domain": true,
  "subdomain_prefix": "@",
  "created_at": "2026-08-02T18:00:00Z"
}</pre>
      </div>
    </div>

    <!-- 2. Verify Domain DNS Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">POST</span>
        <code class="text-sm font-mono text-white">/api/v1/client/domains/{domain_id}/verify-dns</code>
      </div>
      <p class="text-xs text-zinc-400">Queries authoritative root nameservers directly to verify TXT or CNAME DNS propagation.</p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Query Parameters</h4>
        <ul class="text-xs text-zinc-400 space-y-1 font-mono">
          <li><code class="text-emerald-400">record_type</code> (required): <span class="text-zinc-300">"txt"</span> or <span class="text-zinc-300">"cname"</span></li>
        </ul>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Expected Response (200 OK)</h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono">{
  "success": true,
  "cname_verified": true,
  "message": "CNAME record verified successfully!"
}</pre>
      </div>
    </div>

    <!-- 3. List Domains Endpoint -->
    <div class="space-y-4 p-6 bg-zinc-900 border border-zinc-800 rounded-2xl">
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 font-mono text-xs font-bold border border-blue-500/20">GET</span>
        <code class="text-sm font-mono text-white">/api/v1/client/domains</code>
      </div>
      <p class="text-xs text-zinc-400">Fetches all custom domains and subdomains registered by the user.</p>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Expected Response (200 OK)</h4>
        <pre class="p-3 bg-zinc-950 rounded-lg text-xs text-emerald-400 font-mono">[
  {
    "id": 12,
    "name": "brand.com",
    "txt_verified": true,
    "cname_verified": true,
    "is_root_domain": true,
    "subdomain_prefix": "@"
  }
]</pre>
      </div>
    </div>
  </div>
</template>
