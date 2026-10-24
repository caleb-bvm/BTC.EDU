"""Reads the amount a BOLT11 invoice requests; it does not verify the signature."""
import re

from django.conf import settings

MULTIPLIERS = {"": 100_000_000_000, "m": 100_000_000, "u": 100_000, "n": 100, "p": None}


def requested_msat(payment_request):
    value = str(payment_request or "").strip().lower()
    if value.startswith("lightning:"):
        value = value[len("lightning:"):]
    separator = value.rfind("1")
    if separator < 4 or len(value) > 2000 or not re.fullmatch(r"[0-9a-z]+", value):
        return None
    prefix = "lnbcrt" if settings.COMMERCE_PAYMENT_MODE == "regtest" else "lnbc"
    match = re.fullmatch(rf"{prefix}(\d+)([munp]?)", value[:separator])
    if not match or match.group(1).startswith("0"):
        return None
    amount, unit = int(match.group(1)), match.group(2)
    if unit == "p":
        return amount // 10 if amount % 10 == 0 else None
    return amount * MULTIPLIERS[unit]


def normalized(payment_request):
    value = str(payment_request or "").strip()
    return value[len("lightning:"):] if value.lower().startswith("lightning:") else value
