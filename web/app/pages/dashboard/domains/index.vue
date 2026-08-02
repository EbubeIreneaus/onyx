<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: ['auth'] })

useSeoMeta({ title: 'Domains — Onyx' })

const { domains, verifiedDomains, pendingDomains, fetchDomains, createDomain, deleteDomain, pending } = useDomains()

fetchDomains()

const showModal = ref(false)
const newDomain = ref('')
const creating = ref(false)

async function handleCreate() {
  if (!newDomain.value.trim()) return
  creating.value = true
  const result = await createDomain({ name: newDomain.value.trim() })
  creating.value = false
  if (result) {
    showModal.value = false
    newDomain.value = ''
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-NG', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div>
    <!-- Header row -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-base font-semibold text-slate-900 dark:text-white">Custom Domains</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Register and verify custom domains for branded short links.
        </p>
      </div>
      <PermissionButton
        permission="custom:domain"
        label="Add domain"
        icon="i-lucide-plus"
        size="sm"
        @click="showModal = true"
      />
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
      <div class="p-4 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-center">
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ domains.length }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Total domains</p>
      </div>
      <div class="p-4 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-center">
        <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ verifiedDomains.length }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Verified</p>
      </div>
      <div class="p-4 rounded-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-center">
        <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ pendingDomains.length }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Pending verification</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="py-12 flex justify-center">
      <UIcon name="i-lucide-loader-2" class="w-7 h-7 animate-spin text-zinc-500" />
    </div>

    <!-- Empty -->
    <div v-else-if="!domains.length" class="py-14 text-center">
      <div class="inline-flex p-5 rounded-md bg-zinc-50 dark:bg-zinc-950/40 mb-4">
        <UIcon name="i-lucide-globe" class="w-10 h-10 text-zinc-500" />
      </div>
      <p class="text-lg font-semibold text-slate-900 dark:text-white mb-1">No domains registered</p>
      <p class="text-slate-500 text-sm mb-5">Add a custom domain to create branded short links.</p>
      <PermissionButton
        permission="custom:domain"
        label="Add domain"
        icon="i-lucide-plus"
        @click="showModal = true"
      />
    </div>

    <!-- Domains list -->
    <div v-else class="space-y-3">
      <div
        v-for="domain in domains"
        :key="domain.id"
        class="flex items-center gap-4 p-4 bg-white dark:bg-zinc-900 rounded-md border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-200 group"
      >
        <!-- Icon -->
        <div class="shrink-0 w-10 h-10 rounded-md flex items-center justify-center"
          :class="domain.txt_verified ? 'bg-emerald-50 dark:bg-emerald-950/40' : 'bg-amber-50 dark:bg-amber-950/40'"
        >
          <UIcon
            :name="domain.txt_verified ? 'i-lucide-shield-check' : 'i-lucide-shield-alert'"
            class="w-5 h-5"
            :class="domain.txt_verified ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'"
          />
        </div>

        <!-- Domain info -->
        <div class="flex-1 min-w-0">
          <NuxtLink :to="`/dashboard/domains/${domain.id}`" class="text-sm font-semibold text-slate-900 dark:text-white hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors">
            {{ domain.name }}
          </NuxtLink>
          <p class="text-xs text-slate-400 mt-0.5">Added {{ formatDate(domain.created_at) }}</p>
        </div>

        <!-- Status badges -->
        <div class="flex items-center gap-2 shrink-0">
          <UBadge
            :color="domain.txt_verified && domain.cname_verified ? 'success' : 'error'"
            variant="soft"
            size="sm"
            class="capitalize font-medium"
          >
            <UIcon
              :name="domain.txt_verified && domain.cname_verified ? 'i-lucide-check-circle-2' : 'i-lucide-alert-circle'"
              class="w-3.5 h-3.5 mr-1 shrink-0"
            />
            {{ domain.txt_verified && domain.cname_verified ? 'Verified' : 'Unverified' }}
          </UBadge>
        </div>

        <!-- Delete -->
        <UButton
          icon="i-lucide-trash-2"
          size="xs"
          color="error"
          variant="ghost"
          class="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          @click="deleteDomain(domain.id)"
        />
      </div>
    </div>

    <!-- Add Domain Modal -->
    <UModal v-model:open="showModal" title="Add Custom Domain">
      <template #body>
        <div class="space-y-4 p-1">
          <UAlert
            description="Custom domains require TXT DNS verification before use. Onyx subdomains (*.onyx.com) are verified automatically."
            color="info"
            variant="soft"
            icon="i-lucide-info"
          />
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Domain name</label>
            <UInput
              v-model="newDomain"
              placeholder="yourdomain.com or sub.onyx.com"
              icon="i-lucide-globe"
              size="md"
              class="w-full"
              @keydown.enter="handleCreate"
            />
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton color="neutral" variant="ghost" @click="showModal = false; newDomain = ''">Cancel</UButton>
          <UButton :loading="creating" :disabled="!newDomain.trim()" @click="handleCreate">Add domain</UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
