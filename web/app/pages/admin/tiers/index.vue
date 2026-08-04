<script setup lang="ts">
import { availablePermissions } from '@/libs/permission'

definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

useSeoMeta({
  title: 'Manage Tiers & Pricing — Admin'
})

const api = useApi()
const toast = useToast()

interface AdminTier {
  id: number
  tier_id: string
  name: string
  price: number
  permissions: string[]
  max_short_link: string
  link_durability: string
  max_custom_domains: string
  max_onyx_subdomains: string
  max_custom_paths: string
  max_visits_per_shortlink: string
  is_active: boolean
  created_at: string
}

const tiers = ref<AdminTier[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedTier = ref<AdminTier | null>(null)
const submitting = ref(false)

const form = ref({
  name: '',
  price: 0,
  permissions: ['free:link'],
  max_short_link: '100',
  link_durability: '14',
  max_custom_domains: '1',
  max_onyx_subdomains: '1',
  max_custom_paths: '10',
  max_visits_per_shortlink: '1000',
  description: '',
  is_active: true
})

const fetchTiers = async () => {
  loading.value = true
  try {
    tiers.value = await api<AdminTier[]>('/api/v1/admin/tiers')
  } catch (err: any) {
    toast.add({ title: 'Error', description: 'Failed to load subscription tiers', color: 'error' })
  } finally {
    loading.value = false
  }
}

fetchTiers()

const resetForm = () => {
  form.value = {
    name: '',
    price: 0,
    permissions: ['free:link'],
    max_short_link: '100',
    link_durability: '14',
    max_custom_domains: '1',
    max_onyx_subdomains: '1',
    max_custom_paths: '10',
    max_visits_per_shortlink: '1000',
    description: '',
    is_active: true
  }
}

const openCreate = () => {
  resetForm()
  showCreateModal.value = true
}

const handleCreateTier = async () => {
  if (!form.value.name.trim()) return
  submitting.value = true
  try {
    const newTier = await api<AdminTier>('/api/v1/admin/tiers', {
      method: 'POST',
      body: form.value
    })
    tiers.value.push(newTier)
    showCreateModal.value = false
    toast.add({ title: 'Tier Created', description: `Subscription tier '${newTier.name}' created successfully!`, color: 'success' })
  } catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to create tier', color: 'error' })
  } finally {
    submitting.value = false
  }
}

const openEdit = (tier: AdminTier) => {
  selectedTier.value = tier
  form.value = {
    name: tier.name,
    price: Number(tier.price),
    permissions: [...(tier.permissions || [])],
    max_short_link: String(tier.max_short_link),
    link_durability: String(tier.link_durability),
    max_custom_domains: String(tier.max_custom_domains),
    max_onyx_subdomains: String(tier.max_onyx_subdomains),
    max_custom_paths: String(tier.max_custom_paths),
    max_visits_per_shortlink: String(tier.max_visits_per_shortlink),
    description: '',
    is_active: tier.is_active
  }
  showEditModal.value = true
}

const handleUpdateTier = async () => {
  if (!selectedTier.value) return
  submitting.value = true
  try {
    const updated = await api<AdminTier>(`/api/v1/admin/tiers/${selectedTier.value.tier_id}`, {
      method: 'PATCH',
      body: form.value
    })
    const idx = tiers.value.findIndex(t => t.tier_id === selectedTier.value?.tier_id)
    if (idx !== -1) tiers.value[idx] = updated
    showEditModal.value = false
    toast.add({ title: 'Tier Updated', color: 'success' })
  } catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to update tier', color: 'error' })
  } finally {
    submitting.value = false
  }
}

const handleDeleteTier = async (tier: AdminTier) => {
  if (!confirm(`Are you sure you want to delete tier '${tier.name}'?`)) return
  try {
    await api(`/api/v1/admin/tiers/${tier.tier_id}`, { method: 'DELETE' })
    tiers.value = tiers.value.filter(t => t.tier_id !== tier.tier_id)
    toast.add({ title: 'Tier Deleted', color: 'success' })
  } catch (err: any) {
    toast.add({ title: 'Error', description: err?.data?.detail || 'Failed to delete tier', color: 'error' })
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-6 pb-12">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-extrabold text-white flex items-center gap-2">
          <UIcon
            name="i-lucide-layers"
            class="w-6 h-6 text-amber-400"
          />
          Subscription Tiers & Pricing
        </h1>
        <p class="text-xs text-zinc-400 mt-1">
          Configure subscription plans, set tier quotas, assign permissions, and sync with Paystack.
        </p>
      </div>

      <UButton
        icon="i-lucide-plus"
        color="secondary"
        variant="solid"
        size="md"
        @click="openCreate"
      >
        Create New Tier
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

    <!-- Tiers Grid -->
    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-2 gap-6"
    >
      <div
        v-for="t in tiers"
        :key="t.id"
        class="p-6 bg-zinc-900 border border-zinc-800 rounded-2xl space-y-5 shadow-xs relative overflow-hidden"
      >
        <div class="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div>
            <h3 class="text-xl font-extrabold text-white capitalize flex items-center gap-2">
              {{ t.name }}
            </h3>
            <p class="text-2xl font-mono font-extrabold text-amber-400 mt-1">
              ${{ t.price }} <span class="text-xs text-zinc-500 font-sans">/ month</span>
            </p>
          </div>

          <div class="flex items-center gap-2">
            <UBadge
              :color="t.is_active ? 'success' : 'neutral'"
              variant="soft"
              size="xs"
              :label="t.is_active ? 'Active' : 'Disabled'"
            />
            <UButton
              icon="i-lucide-edit-3"
              color="neutral"
              variant="ghost"
              size="xs"
              @click="openEdit(t)"
            />
            <UButton
              icon="i-lucide-trash-2"
              color="error"
              variant="ghost"
              size="xs"
              @click="handleDeleteTier(t)"
            />
          </div>
        </div>

        <!-- Quotas -->
        <div class="grid grid-cols-2 gap-3 text-xs font-mono">
          <div class="p-2.5 bg-zinc-950 rounded-xl border border-zinc-800">
            <span class="text-zinc-500 block text-[10px] font-sans">MAX LINKS</span>
            <span class="text-white font-bold">{{ t.max_short_link }}</span>
          </div>
          <div class="p-2.5 bg-zinc-950 rounded-xl border border-zinc-800">
            <span class="text-zinc-500 block text-[10px] font-sans">DURABILITY</span>
            <span class="text-white font-bold">{{ t.link_durability }} days</span>
          </div>
          <div class="p-2.5 bg-zinc-950 rounded-xl border border-zinc-800">
            <span class="text-zinc-500 block text-[10px] font-sans">CUSTOM DOMAINS</span>
            <span class="text-white font-bold">{{ t.max_custom_domains }}</span>
          </div>
          <div class="p-2.5 bg-zinc-950 rounded-xl border border-zinc-800">
            <span class="text-zinc-500 block text-[10px] font-sans">VISITS LIMIT</span>
            <span class="text-white font-bold">{{ t.max_visits_per_shortlink }}</span>
          </div>
        </div>

        <!-- Permissions Tags -->
        <div class="space-y-2">
          <span class="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Granted Permissions</span>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="p in t.permissions"
              :key="p"
              class="px-2 py-0.5 rounded-md bg-zinc-950 text-emerald-400 font-mono text-[11px] border border-zinc-800"
            >
              {{ p }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tier Modal -->
    <UModal
      v-model:open="showCreateModal"
      title="Create Subscription Tier"
    >
      <template #body>
        <div class="space-y-4 max-h-[70vh] overflow-y-auto p-1 text-xs">
          <div>
            <label class="block text-zinc-400 mb-1 font-bold">Tier Name</label>
            <UInput
              v-model="form.name"
              placeholder="e.g. pro, business, enterprise"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Price (₦ NGN)</label>
              <UInput
                v-model.number="form.price"
                type="number"
                step="0.01"
              />
            </div>
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Max Short Links</label>
              <UInput
                v-model="form.max_short_link"
                placeholder="100 or unlimited"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Link Durability (days)</label>
              <UInput
                v-model="form.link_durability"
                placeholder="14 or forever"
              />
            </div>
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Max Custom Domains</label>
              <UInput
                v-model="form.max_custom_domains"
                placeholder="1 or unlimited"
              />
            </div>
          </div>

          <div>
            <label class="block text-zinc-400 mb-2 font-bold">Select Tier Permissions</label>
            <div class="space-y-2">
              <label
                v-for="p in availablePermissions"
                :key="p.value"
                class="flex items-center gap-2 text-zinc-300 cursor-pointer"
              >
                <input
                  v-model="form.permissions"
                  type="checkbox"
                  :value="p.value"
                  class="rounded bg-zinc-800 border-zinc-700 text-amber-500"
                >
                <span>{{ p.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-3 w-full">
          <UButton
            color="neutral"
            variant="soft"
            @click="showCreateModal = false"
          >
            Cancel
          </UButton>
          <UButton
            color="primary"
            :loading="submitting"
            @click="handleCreateTier"
          >
            Save & Sync Paystack
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- Edit Tier Modal -->
    <UModal
      v-model:open="showEditModal"
      title="Edit Subscription Tier"
    >
      <template #body>
        <div class="space-y-4 max-h-[70vh] overflow-y-auto p-1 text-xs">
          <div>
            <label class="block text-zinc-400 mb-1 font-bold">Tier Name</label>
            <UInput v-model="form.name" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Price ($ USD)</label>
              <UInput
                v-model.number="form.price"
                type="number"
                step="0.01"
              />
            </div>
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Max Short Links</label>
              <UInput v-model="form.max_short_link" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Link Durability (days)</label>
              <UInput v-model="form.link_durability" />
            </div>
            <div>
              <label class="block text-zinc-400 mb-1 font-bold">Max Custom Domains</label>
              <UInput v-model="form.max_custom_domains" />
            </div>
          </div>

          <div>
            <label class="block text-zinc-400 mb-2 font-bold">Select Tier Permissions</label>
            <div class="space-y-2">
              <label
                v-for="p in availablePermissions"
                :key="p.value"
                class="flex items-center gap-2 text-zinc-300 cursor-pointer"
              >
                <input
                  v-model="form.permissions"
                  type="checkbox"
                  :value="p.value"
                  class="rounded bg-zinc-800 border-zinc-700 text-amber-500"
                >
                <span>{{ p.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-3 w-full">
          <UButton
            color="neutral"
            variant="soft"
            @click="showEditModal = false"
          >
            Cancel
          </UButton>
          <UButton
            color="primary"
            :loading="submitting"
            @click="handleUpdateTier"
          >
            Update & Sync Paystack
          </UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
