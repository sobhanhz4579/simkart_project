# wallet/zarinpal.py
import requests


class ZarinPal:
    def __init__(self, merchant_id, callback_url):
        self.merchant_id = merchant_id
        self.callback_url = callback_url
        self.request_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        self.verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        self.start_pay_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def send_request(self, amount, description, email):
        try:
            amount = float(amount)
            if amount <= 0:
                return {"status": "error", "message": "مبلغ باید مثبت باشد", "error_code": "INVALID_AMOUNT"}
        except (ValueError, TypeError):
            return {"status": "error", "message": "مبلغ نامعتبر است", "error_code": "INVALID_AMOUNT"}

        rial_amount = int(round(amount * 10))

        data = {"merchant_id": self.merchant_id, "amount": rial_amount, "description": description,
                "callback_url": self.callback_url,
                "metadata": {"email": email}}
        response = requests.post(self.request_url, json=data)
        result = response.json()
        if result.get("data", {}).get("code") == 100:
            authority = result["data"]["authority"]
            return {"status": "success", "authority": authority, "payment_url": f"{self.start_pay_url}{authority}"}
        return {"status": "error", "message": result.get("errors", {}).get("message", "خطا"),
                "error_code": result.get("errors", {}).get("code")}

    def verify(self, authority, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                return {"status": "error", "message": "مبلغ باید مثبت باشد"}
        except (ValueError, TypeError):
            return {"status": "error", "message": "مبلغ نامعتبر است"}

        rial_amount = int(round(amount * 10))

        data = {"merchant_id": self.merchant_id, "amount": rial_amount, "authority": authority}
        response = requests.post(self.verify_url, json=data)
        result = response.json()
        if result.get("data", {}).get("code") == 100:
            return {"status": "success", "ref_id": result["data"]["ref_id"]}
        return {"status": "error", "message": result.get("errors", {}).get("message", "خطای ناشناخته")}
