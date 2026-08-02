<script setup lang="ts">
const features = [
  {
    icon: 'i-lucide-link-2',
    title: 'Smart Short Links',
    description: 'Generate branded short links instantly. Custom slugs, expiration dates, and per-link analytics included.',
    color: 'zinc',
  },
  {
    icon: 'i-lucide-globe',
    title: 'Custom Domains',
    description: 'Use your own domain for a professional look. Full DNS verification, CNAME support, and multi-domain management.',
    color: 'indigo',
  },
  {
    icon: 'i-lucide-bar-chart-3',
    title: 'Deep Analytics',
    description: 'Track every click with device, location, referrer, and time data. Monthly visitor trends at a glance.',
    color: 'blue',
  },
  {
    icon: 'i-lucide-qr-code',
    title: 'QR Code Generator',
    description: 'Auto-generate high-resolution QR codes for every link. Perfect for print, packaging, and physical marketing.',
    color: 'zinc',
  },
  {
    icon: 'i-lucide-code-2',
    title: 'Developer API',
    description: 'Full REST API with SDK support. Integrate Onyx into your app, CI pipeline, or automation workflow.',
    color: 'indigo',
  },
  {
    icon: 'i-lucide-shield-check',
    title: 'Enterprise Security',
    description: 'TXT-verified domain ownership, link expiration controls, and rate limiting protect your brand at every layer.',
    color: 'blue',
  },
]

const colorMap: Record<string, string> = {
  zinc: 'bg-zinc-100 dark:bg-zinc-950/50 text-zinc-700 dark:text-zinc-300',
  indigo: 'bg-indigo-100 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300',
  blue: 'bg-blue-100 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300',
}
</script>

<template>
  <section id="features" class="py-24 px-4 sm:px-6">
    <div class="max-w-7xl mx-auto">
      <!-- Section header -->
      <div class="text-center mb-16">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-950/50 text-zinc-700 dark:text-zinc-300 text-sm font-medium mb-4">
          <UIcon name="i-lucide-sparkles" class="w-4 h-4" />
          Everything you need
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-slate-900 dark:text-white mb-4">
          Built for scale, designed for<br>
          <span class="gradient-text">simplicity</span>
        </h2>
        <p class="text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">
          Whether you're a solo creator or an enterprise team, Onyx grows with you. Every feature you need, nothing you don't.
        </p>
      </div>

      <!-- Feature grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(feature, i) in features"
          :key="feature.title"
          class="group relative p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-lg hover:shadow-zinc-500/10 transition-all duration-300"
          :style="{ animationDelay: `${i * 80}ms` }"
        >
          <!-- Icon -->
          <div
            class="inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4 transition-transform duration-300 group-hover:scale-110"
            :class="colorMap[feature.color]"
          >
            <UIcon :name="feature.icon" class="w-6 h-6" />
          </div>

          <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            {{ feature.title }}
          </h3>
          <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            {{ feature.description }}
          </p>

          <!-- Hover glow -->
          <div class="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
            style="background: radial-gradient(circle at 50% 0%, rgba(124,58,237,0.04), transparent 70%);" />
        </div>
      </div>
    </div>
  </section>
</template>
