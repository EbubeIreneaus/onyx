from setting import settings
import uuid
import json
import urllib.request
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import httpx
from models.db import SessionLocal
from models.redirect import Redirect as RedirectModel, RedirectVisitors as RedirectVisitorModel
from models.user import User, Subscription
from libs.logger import logger
from libs.redis import redis
import asyncio  

async def add_domain_alias(ctx, domain_name:str):

    async with httpx.AsyncClient() as client:
        netlify_url = f"https://api.netlify.com/api/v1/sites/{settings.NETLIFY_SITE_ID}"

        headers = {
            "Authorization": f"Bearer {settings.NETLIFY_SECRET_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "domain": domain_name
        }
        r = await client.get(netlify_url, headers=headers)
        if not r.status_code == 200:
            logger.error(f"Error while fetching data from Netlify: {r.status_code}")
            raise Exception("Error while fetching data from Netlify")
        
        existing_aliases = r.json().get("domain_aliases", [])
        if domain_name in existing_aliases:
            logger.info(f"Domain alias {domain_name} already exists")
            return
        existing_aliases.append(domain_name)

        r = await client.patch(netlify_url, headers=headers, json={"domain_aliases": existing_aliases})
        if not r.status_code == 200:
            logger.error(f"Error while updating domain alias: {domain_name} - {r.text}")
            raise Exception("Error while updating domain alias")
        logger.info(f"Domain alias {domain_name} updated successfully")

async def delete_domain_alias(ctx, domain_name:str):
    async with httpx.AsyncClient() as client:
        netlify_url = f"https://api.netlify.com/api/v1/sites/{settings.NETLIFY_SITE_ID}"

        headers = {
            "Authorization": f"Bearer {settings.NETLIFY_SECRET_TOKEN}",
            "Content-Type": "application/json"
        }
        
        r = await client.get(netlify_url, headers=headers)
        if not r.status_code == 200:
            logger.error(f"Error while fetching data from Netlify: {r.status_code}")
            raise Exception("Error while fetching data from Netlify")
        
        existing_aliases = r.json().get("domain_aliases", [])
        if domain_name not in existing_aliases:
            logger.info(f"Domain alias {domain_name} not found")
            return
        existing_aliases.remove(domain_name)

        r = await client.patch(netlify_url, headers=headers, json={"domain_aliases": existing_aliases})
        if not r.status_code == 200:
            logger.error(f"Error while deleting domain alias: {domain_name} - {r.text}")
            raise Exception("Error while deleting domain alias")
        logger.info(f"Domain alias {domain_name} deleted successfully")

