from dns.edns import COOKIE
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    APP_ENV: str = "development"
    MIN_ALLOWED_SHORT_LINKS: int = 5 #Minimum short link any tier user could create
    DOMAIN_NAME: str = "onyx.com"

    ONYX_ADMIN_PASS: str
    ONYX_ADMIN_EMAIL: str
    
    PAYSTACK_SECRET: str
    PAYSTACK_PUBLIC: str

    REDIS_URL: str

    MAIL_USER: str
    MAIL_HOST: str 
    MAIL_PORT: int = 465
    MAIL_PASS: str
    MAIL_SSL_TLS: bool = True
    MAIL_STARTTLS: bool = False
    MAIL_FROM: str
    MAIL_FROM_NAME: str

    CLOUDINARY_NAME: str
    CLOUDINARY_SECRET: str
    CLOUDINARY_KEY: str
    IMAGE_FOLDER: str = "16vmart"

    STRIPE_SECRET: str
    STRIPE_HOOK_SECRET: str


    class Config:
        env_file = ".env"

settings = Settings()