from enum import Enum

class AppPermission(Enum):
    CUSTOM_DOMAIN="custom:domain"
    ONYX_SUBDOMAIN="onyx:subdomain"
    FREE_LINK="free:link"
    VISITOR_ANALYTICS="visitor:analytics"
    CUSTOM_PATH="custom:path"
    API_ACCESS="api:access"
    QRIMAGE="qrimage"
    SDK="sdk"


class AdminPermission(Enum):
    MANAGE_USERS="manage:users"
    MANAGE_TIERS="manage:tiers"
    MANAGE_DOMAINS="manage:domains"
    MANAGE_REDIRECTS="manage:redirects"
    MANAGE_SESSIONS="manage:sessions"
    MANAGE_SUBSCRIPTIONS="manage:subscriptions"
    MANAGE_AI_ANALYSIS="manage:ai:analysis"
    MANAGE_API_ACCESS="manage:api:access"
    MANAGE_CUSTOM_DOMAINS="manage:custom:domains"
    MANAGE_ONYX_SUBDOMAINS="manage:onyx:subdomains"
    MANAGE_CUSTOM_PATHS="manage:custom:paths"
    MANAGE_ALL="manage:all"
  