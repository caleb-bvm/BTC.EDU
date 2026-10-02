"""Prueba local de facturación y pago. Guarda claves solo en .local/."""
import json
import secrets
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
credentials = ROOT / '.local' / 'demo-credentials.json'

def request(client, method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()

with httpx.Client(base_url='http://127.0.0.1:5000', timeout=20, trust_env=False) as client:
    if credentials.exists():
        account = json.loads(credentials.read_text())
        request(client, 'POST', '/api/v1/auth', json=account)
    else:
        account = {'username': 'demo_admin', 'password': secrets.token_urlsafe(24)}
        request(client, 'PUT', '/api/v1/auth/first_install', json={
            **account, 'password_repeat': account['password']
        })
        credentials.write_text(json.dumps(account), encoding='utf-8')
    receiver = request(client, 'POST', '/api/v1/wallet', json={'name': 'Contenido de prueba'})
    payer = request(client, 'POST', '/api/v1/wallet', json={'name': 'Comprador simulado'})
    request(client, 'PUT', '/users/api/v1/balance', json={'id': payer['id'], 'amount': 1000})
    invoice = request(client, 'POST', '/api/v1/payments',
                      headers={'X-Api-Key': receiver['inkey']},
                      json={'out': False, 'amount': 100, 'memo': 'Guia premium de prueba', 'expiry': 900})
    status_path = '/api/v1/payments/' + invoice['payment_hash']
    headers = {'X-Api-Key': receiver['inkey']}
    before = request(client, 'GET', status_path, headers=headers)
    assert not before['paid'], 'Factura inesperadamente pagada'
    request(client, 'POST', '/api/v1/payments',
            headers={'X-Api-Key': payer['adminkey']},
            json={'out': True, 'bolt11': invoice['bolt11']})
    for _ in range(20):
        after = request(client, 'GET', status_path, headers=headers)
        if after['paid']:
            break
        time.sleep(0.2)
    assert after['paid'], 'No se confirmo el pago'
    print('OK: factura de 100 sats simulados, pendiente -> pagada; verificada por API.')
