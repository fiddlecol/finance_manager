import requests
import json
from datetime import datetime
import os
from requests.auth import HTTPBasicAuth

class STKPushHandler:
    """Handle M-Pesa STK Push payment requests"""
    
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY', '')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', '')
        self.business_shortcode = os.getenv('MPESA_SHORTCODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY', '')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
        
        # Environment: sandbox or production
        self.environment = os.getenv('MPESA_ENV', 'sandbox')
        
        if self.environment == 'sandbox':
            self.auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        else:
            self.auth_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            response = requests.get(
                self.auth_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, account_reference, description):
        """
        Initiate STK Push for payment
        
        Args:
            phone_number: Customer's phone number (format: 254XXXXXXXXX)
            amount: Amount to charge (integer)
            account_reference: Unique reference (contribution ID)
            description: Payment description
        
        Returns:
            dict: Response from M-Pesa with CheckoutRequestID
        """
        
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        data_to_encode = f"{self.business_shortcode}{self.passkey}{timestamp}"
        import base64
        password = base64.b64encode(data_to_encode.encode()).decode()
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": str(account_reference),
            "TransactionDesc": description
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.stk_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK Push: {e}")
            return {'error': str(e)}
    
    def validate_callback(self, callback_data):
        """
        Validate payment callback from M-Pesa
        
        Args:
            callback_data: The callback data from M-Pesa
        
        Returns:
            dict: Parsed callback data or error
        """
        try:
            # M-Pesa sends data in nested structure
            result = callback_data.get('Body', {}).get('stkCallback', {})
            
            return {
                'checkout_request_id': result.get('CheckoutRequestID'),
                'result_code': result.get('ResultCode'),
                'result_desc': result.get('ResultDesc'),
                'merchant_request_id': result.get('MerchantRequestID'),
                'callback_metadata': result.get('CallbackMetadata', {})
            }
        except (KeyError, TypeError) as e:
            print(f"Error validating callback: {e}")
            return {'error': str(e)}

# Initialize handler
stk_handler = STKPushHandler()
