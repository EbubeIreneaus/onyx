export const key_pages = [
  'login',
  'dashboard',
  'dashboard/domain',
  'dashboard/domains/*',
  'dashboard/links',
  'dashboard/redirect/*',
  'dashboard/settings',
  'dashboard/developer',
  'admin',
  'admin/domains',
  'admin/links',
  'admin/tiers',
  'admin/users',
  'signup'
]

/**
 * Checks if a user-provided custom slug/path matches or conflicts with any system key pages.
 * Reserved paths only apply when creating a link on the default/primary domain.
 */
export function isReservedPath(slug: string, domain?: string, mainDomain = 'localhost:3000'): boolean {
  if (!slug) return false

  // If a custom domain or custom subdomain is provided (and it's not the primary domain), reserved path checks don't block it
  if (domain && domain.trim().toLowerCase() !== mainDomain.trim().toLowerCase()) {
    return false
  }

  const normalized = slug.trim().replace(/^\/+|\/+$/g, '').toLowerCase()

  for (const page of key_pages) {
    const cleanPage = page.trim().replace(/^\/+|\/+$/g, '').toLowerCase()

    if (cleanPage.endsWith('/*')) {
      const prefix = cleanPage.slice(0, -2)
      if (normalized === prefix || normalized.startsWith(`${prefix}/`)) {
        return true
      }
    } else if (normalized === cleanPage) {
      return true
    }
  }

  return false
}
