from setting import settings

KEY_PAGES = [
    "login",
    "dashboard",
    "dashboard/domain",
    "dashboard/domains/*",
    "dashboard/links",
    "dashboard/redirect/*",
    "dashboard/settings",
    "dashboard/developer",
    "admin",
    "admin/domains",
    "admin/links",
    "admin/tiers",
    "admin/users",
    "signup",
]


def is_reserved_path(slug: str, domain: str = None) -> bool:
    """Checks if a user-provided custom slug/path matches or conflicts with any system key pages.

    Reserved path validation only applies when creating a link on the primary/default application domain.
    Custom domains and user-defined subdomains do not block system route paths.
    """
    if not slug:
        return False

    main_domain = settings.DOMAIN_NAME.lower().strip()
    if domain:
        clean_domain = domain.lower().strip()
        if clean_domain != main_domain:
            return False

    normalized = slug.strip().strip("/").lower()

    for page in KEY_PAGES:
        clean_page = page.strip().strip("/").lower()
        if clean_page.endswith("/*"):
            prefix = clean_page[:-2]
            if normalized == prefix or normalized.startswith(f"{prefix}/"):
                return True
        elif normalized == clean_page:
            return True

    return False
