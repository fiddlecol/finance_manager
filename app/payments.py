import requests
import json
from datetime import datetime
import os
from requests.auth import HTTPBasicAuth
import base64

from app import db
from app.models import Contribution, PaymentCallback, Event

class STKPushHandler:
    """Handle M-Pesa STK Push payment requests (Till)"""
    
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY', '')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', '')
        self.business_shortcode = os.getenv('MPESA_SHORTCODE', '')  # Till number
        self.passkey = os.getenv('MPESA_PASSKEY', '')
        self.callback_url = os.getenv(
            'MPESA_CALLBACK_URL',
            'https://contribution.fiddawg.co.ke/api/payment/callback'
        )
        self.environment = os.getenv('MPESA_ENV', 'sandbox')
        
        if self.environment == 'sandbox':
            self.auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        else:
            self.auth_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            self.stk_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    
    def get_access_token(self):
        try:
            if not self.consumer_key or not self.consumer_secret:
                print("MPESA consumer key/secret not set.")
                return None
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
    
    def initiate_stk_push(self, phone_number, amount, contribution_id, description):
        """Initiate STK Push and store CheckoutRequestID in Contribution"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        if not self.passkey:
            return {'error': 'MPESA passkey missing'}
        
        # Normalize phone
        phone_number = str(phone_number).strip()
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('7'):
            phone_number = '254' + phone_number[-9:]
        elif phone_number.startswith('254') and len(phone_number) == 12:
            pass
        else:
            return {'error': 'Invalid phone number format'}
        
        # Generate password
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        
        # Shorten AccountReference to 12 chars max for sandbox
        account_ref = f"CONTRIB{contribution_id}"[:12]
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # Sandbox compatible
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_ref,
            "TransactionDesc": description
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            payload_safe = {k: v for k, v in payload.items() if k != 'Password'}
            print("Initiating STK Push. Payload (safe):", json.dumps(payload_safe, indent=2))
            
            response = requests.post(self.stk_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            resp_json = response.json()
            
            # Save CheckoutRequestID in contribution
            if 'CheckoutRequestID' in resp_json:
                contribution = Contribution.query.get(contribution_id)
                if contribution:
                    contribution.transaction_id = resp_json['CheckoutRequestID']
                    db.session.commit()
            
            return resp_json
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK Push: {e}")
            return {'error': str(e)}
    
    def validate_callback(self, callback_data):
        """Parse M-Pesa callback and auto-update contribution and event"""
        try:
            result = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_id = result.get('CheckoutRequestID')
            result_code = result.get('ResultCode', -1)
            result_desc = result.get('ResultDesc')
            
            # Store raw callback
            callback = PaymentCallback(
                raw_response=callback_data,
                status='failed' if result_code != 0 else 'success',
                mpesa_receipt_number=None,
                phone_number=None,
                amount=None,
                contribution_id=None
            )
            
            if result_code == 0:
                metadata_items = result.get('CallbackMetadata', {}).get('Item', [])
                payment_data = {}
                for item in metadata_items:
                    name = item.get('Name')
                    value = item.get('Value')
                    if name == 'Amount':
                        payment_data['amount'] = value
                    elif name == 'MpesaReceiptNumber':
                        payment_data['receipt'] = value
                    elif name == 'PhoneNumber':
                        payment_data['phone'] = value
                
                contribution = Contribution.query.filter_by(transaction_id=checkout_id).first()
                if contribution:
                    contribution.status = 'completed'
                    contribution.transaction_id = payment_data.get('receipt')
                    if contribution.event:
                        contribution.event.current_amount += contribution.amount
                    callback.contribution_id = contribution.id
                    db.session.commit()
                
                callback.mpesa_receipt_number = payment_data.get('receipt')
                callback.phone_number = payment_data.get('phone')
                callback.amount = payment_data.get('amount')
            
            db.session.add(callback)
            db.session.commit()
            
            return {
                'checkout_request_id': checkout_id,
                'result_code': result_code,
                'result_desc': result_desc
            }
        except Exception as e:
            print(f"Error validating callback: {e}")
            return {'error': str(e)}

# Singleton instance
stk_handler = STKPushHandler()
