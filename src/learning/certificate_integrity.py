"""Versioned, reproducible certificate records. This is a digest, not a signature."""
import hashlib
import hmac
import json
from datetime import UTC


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def certificate_record(certificate):
    return {
        "schema": "btc.edu.certificate.v1",
        "id": str(certificate.pk),
        "student_name": certificate.student_name,
        "course_title": certificate.course_title,
        "creator_name": certificate.creator_name,
        "version": certificate.enrollment.version.number,
        "issued_at": certificate.issued_at.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "evidence_sha256": hashlib.sha256(canonical_json(certificate.evidence)).hexdigest(),
    }


def certificate_bytes(certificate):
    return canonical_json(certificate_record(certificate))


def certificate_digest(certificate):
    return hashlib.sha256(certificate_bytes(certificate)).hexdigest()


def certificate_intact(certificate):
    stored = certificate.fingerprint
    return (isinstance(stored, str) and len(stored) == 64 and all(char in "0123456789abcdef" for char in stored)
            and hmac.compare_digest(stored, certificate_digest(certificate)))
