from typing import Optional, Dict, Any
from httpx import AsyncClient, HTTPStatusError
from setting import settings
from libs.logger import logger

class PaystackPaymentService:
    def __init__(self):
        self.PAYSTACK_BASE_URL = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET}",
            "Content-Type": "application/json",
        }

    async def create_customer(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
    ) -> Dict[str, Any]:
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }
        try:
            async with AsyncClient() as client:
                res = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/customer",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error creating Paystack customer for {email}: {e}")
            return {"status": False, "message": str(e)}

    async def create_subscription_plan(
        self,
        name: str,
        amount_naira: float,
        interval: str = "monthly",
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        amount_in_kobo = int(float(amount_naira) * 100)
        payload = {
            "name": name,
            "interval": interval.lower(),
            "amount": amount_in_kobo,
            "currency": "NGN",
        }
        if description:
            payload["description"] = description

        try:
            async with AsyncClient() as client:
                res = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/plan",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error creating Paystack plan '{name}': {e}")
            return {"status": False, "message": str(e)}

    async def update_subscription_plan(
        self,
        plan_code: str,
        name: Optional[str] = None,
        amount_naira: Optional[float] = None,
        interval: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {}
        if name is not None:
            payload["name"] = name
        if amount_naira is not None:
            payload["amount"] = int(float(amount_naira) * 100)
        if interval is not None:
            payload["interval"] = interval.lower()
        if description is not None:
            payload["description"] = description

        try:
            async with AsyncClient() as client:
                res = await client.put(
                    f"{self.PAYSTACK_BASE_URL}/plan/{plan_code}",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error updating Paystack plan '{plan_code}': {e}")
            return {"status": False, "message": str(e)}

    async def initialize_transaction(
        self,
        email: str,
        amount_naira: float,
        plan_code: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "email": email,
            "amount": int(float(amount_naira) * 100),
            "currency": "NGN",
        }
        if plan_code:
            payload["plan"] = plan_code
        if callback_url:
            payload["callback_url"] = callback_url
        if metadata:
            payload["metadata"] = metadata

        try:
            async with AsyncClient() as client:
                res = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/transaction/initialize",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error initializing Paystack transaction for {email}: {e}")
            return {"status": False, "message": str(e)}

    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        try:
            async with AsyncClient() as client:
                res = await client.get(
                    f"{self.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
                    headers=self.headers,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error verifying Paystack transaction '{reference}': {e}")
            return {"status": False, "message": str(e)}

    async def fetch_subscription(self, subscription_code: str) -> Dict[str, Any]:
        try:
            async with AsyncClient() as client:
                res = await client.get(
                    f"{self.PAYSTACK_BASE_URL}/subscription/{subscription_code}",
                    headers=self.headers,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error fetching Paystack subscription '{subscription_code}': {e}")
            return {"status": False, "message": str(e)}

    async def create_subscription(
        self,
        customer: str,
        plan: str,
        authorization: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "customer": customer,
            "plan": plan,
        }
        if authorization:
            payload["authorization"] = authorization
        if start_date:
            payload["start_date"] = start_date

        try:
            async with AsyncClient() as client:
                res = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/subscription",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error creating Paystack subscription for customer '{customer}': {e}")
            return {"status": False, "message": str(e)}

    async def disable_subscription(self, code: str, token: str) -> Dict[str, Any]:
        payload = {
            "code": code,
            "token": token,
        }
        try:
            async with AsyncClient() as client:
                res = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/subscription/disable",
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.exception(f"Error disabling Paystack subscription '{code}': {e}")
            return {"status": False, "message": str(e)}

paystack = PaystackPaymentService()