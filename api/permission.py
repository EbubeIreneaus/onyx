from enum import Enum

class AppPermission(Enum):
    CREATE_CUSTOM_DOMAIN="create:custom:domain"
    USE_ONYX_SUBDOMAIN="use:onyx:subdomain"
    USE_CUSTOM_PATH="use:custom:path"
    USE_AI_ANALYSIS="use:ai:analysis"
    API_ACCESS="api:access"


