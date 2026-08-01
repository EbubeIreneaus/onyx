from httpx import AsyncClient
from setting import settings

class PaystackPaymentService:
    def __init__(self):
        self.PAYSTACK_BASE_URL = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET}",
            "Content-Type": "application/json",
        }
    
    async def create_subscription_plan(self, plan_data: dict):
        try:
            async with AsyncClient() as client:
                response = await client.post(
                    f"{self.PAYSTACK_BASE_URL}/plan",
                    headers=self.headers,
                    json=plan_data,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    def create_subscription(self):
        pass

    def verify_subscription(self):
        pass

    def create_subscription_charge(self):
        pass

    def verify_subscription_charge(self):
        pass

    def create_customer(self):
        pass

    