#!/usr/bin/env python3
"""Utility to test M-Pesa credentials and STK Push payload locally.

Usage examples:
  # show computed password and masked env
  python scripts/test_mpesa.py --show

  # get access token
  python scripts/test_mpesa.py --token

  # perform an STK Push (will actually call Safaricom)
  python scripts/test_mpesa.py --stk --phone 2547XXXXXXXX --amount 10 --account TEST
"""
import os
import sys
import argparse
import base64
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()


def mask(s):
    if not s:
        return None
    s = str(s)
    if len(s) <= 6:
        return '****'
    return s[:3] + '***' + s[-3:]


def get_auth_url(env):
    if env == 'production':
        return 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    return 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


def compute_password(shortcode, passkey, timestamp=None):
    if not timestamp:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode(), timestamp


def get_token(consumer_key, consumer_secret, env):
    url = get_auth_url(env)
    try:
        r = requests.get(url, auth=(consumer_key, consumer_secret), timeout=10)
        print('Auth status:', r.status_code)
        try:
            print('Auth response:', r.json())
        except Exception:
            print('Auth response text:', r.text)
        if r.status_code == 200:
            return r.json().get('access_token')
    except requests.RequestException as e:
        print('Error getting token:', e)
    return None


def do_stk_push(token, stk_url, payload):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    safe = {k: v for k, v in payload.items() if k != 'Password'}
    print('STK Payload (safe):', safe)
    try:
        r = requests.post(stk_url, json=payload, headers=headers, timeout=10)
        print('STK status:', r.status_code)
        try:
            print('STK response:', r.json())
        except Exception:
            print('STK response text:', r.text)
        return r
    except requests.RequestException as e:
        print('Error performing STK Push:', e)
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--show', action='store_true', help='Show masked env and computed password')
    p.add_argument('--token', action='store_true', help='Request access token')
    p.add_argument('--stk', action='store_true', help='Perform STK Push')
    p.add_argument('--phone')
    p.add_argument('--amount', type=int, default=1)
    p.add_argument('--account', default='TEST')
    args = p.parse_args()

    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    env = os.getenv('MPESA_ENV', 'sandbox')
    callback = os.getenv('MPESA_CALLBACK_URL', 'https://example.com/callback')
    stk_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest' if env != 'production' else 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    if args.show:
        password, ts = compute_password(shortcode or '', passkey or '')
        print('MPESA_ENV=', repr(env))
        print('MPESA_CONSUMER_KEY=', mask(consumer_key))
        print('MPESA_CONSUMER_SECRET=', mask(consumer_secret))
        print('MPESA_SHORTCODE=', repr(shortcode))
        print('MPESA_PASSKEY=', repr(passkey))
        print('Computed Timestamp:', ts)
        print('Computed Password (base64):', password)
        return

    if args.token or args.stk:
        if not consumer_key or not consumer_secret:
            print('Missing consumer key/secret in environment')
            sys.exit(1)
        token = get_token(consumer_key, consumer_secret, env)
        print('Access token:', mask(token))
        if not token:
            print('Failed to obtain token; aborting.')
            sys.exit(1)

    if args.token and not args.stk:
        return

    if args.stk:
        if not args.phone:
            print('Provide --phone in 2547XXXXXXXX format')
            sys.exit(1)
        if not shortcode or not passkey:
            print('MPESA_SHORTCODE or MPESA_PASSKEY missing')
            sys.exit(1)

        password, ts = compute_password(shortcode, passkey)
        payload = {
            'BusinessShortCode': shortcode,
            'Password': password,
            'Timestamp': ts,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': args.amount,
            'PartyA': args.phone,
            'PartyB': shortcode,
            'PhoneNumber': args.phone,
            'CallBackURL': callback,
            'AccountReference': args.account,
            'TransactionDesc': 'Test'
        }
        do_stk_push(token, stk_url, payload)


if __name__ == '__main__':
    main()
