<script setup lang="ts">
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap' }
  ],
  htmlAttrs: { lang: 'en' }
})

useSeoMeta({
  title: 'Onyx — Smart URL Shortener & Link Management',
  description: 'Shorten, track, and manage your links with Onyx. Custom domains, detailed analytics, QR codes, and team features for modern businesses.',
  ogTitle: 'Onyx — Smart URL Shortener & Link Management',
  ogDescription: 'Shorten, track, and manage your links with Onyx. Custom domains, detailed analytics, QR codes, and team features for modern businesses.',
  ogImage: '/og-image.png',
  twitterCard: 'summary_large_image',
  twitterTitle: 'Onyx — Smart URL Shortener',
  twitterDescription: 'Shorten, track, and manage your links with Onyx.'
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
