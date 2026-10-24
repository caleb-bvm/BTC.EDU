import hashlib
import io
import uuid

import httpx
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from commerce.models import Entitlement
from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from . import test_essential, timestamps
from .models import (
    CertificateTimestamp,
    CourseReview,
    LearningPath,
    PathCompletion,
    PathCourse,
    PracticeDraft,
)
from .paths import issue_path_credential, path_digest, path_progress
from .practices import review_delivery, submit_delivery
from .reviews import rating_summary, reply_review, review_basis, save_review
from .services import enroll, save_progress
from .showcase import gallery_items, set_showcase

CALENDAR = "https://alice.btc.calendar.opentimestamps.org"


def pending_reply(uri=CALENDAR):
    payload = io.BytesIO()
    timestamps.write_varbytes(payload, uri.encode())
    out = io.BytesIO()
    out.write(b"\xf0")
    timestamps.write_varbytes(out, b"calendar-nonce")
    out.write(b"\x08\x00" + timestamps.PENDING)
    timestamps.write_varbytes(out, payload.getvalue())
    return out.getvalue()


def bitcoin_reply(height=860000):
    payload = io.BytesIO()
    timestamps.write_varuint(payload, height)
    out = io.BytesIO()
    out.write(b"\xf1")
    timestamps.write_varbytes(out, b"merkle")
    out.write(b"\x08\x00" + timestamps.BITCOIN)
    timestamps.write_varbytes(out, payload.getvalue())
    return out.getvalue()


@override_settings(CERTIFICATE_OTS_CALENDARS=[CALENDAR + "/"], CERTIFICATE_TIMESTAMPS=True)
class TimestampTests(TestCase):
    setUp = test_essential.EssentialTests.setUp
    complete = test_essential.EssentialTests.complete
    certificate = test_essential.EssentialTests.certificate

    def test_proof_round_trip_and_bitcoin_upgrade(self):
        calls = []
        def handler(request):
            calls.append((request.method, request.url.path))
            if request.method == "POST":
                self.assertEqual(len(request.content), 32)
                return httpx.Response(200, content=pending_reply())
            return httpx.Response(200, content=bitcoin_reply())
        transport = httpx.MockTransport(handler)
        digest = hashlib.sha256(b"datos").digest()
        proof, calendars = timestamps.submit(digest, transport)
        self.assertEqual(calendars, [CALENDAR + "/"])
        self.assertTrue(proof.startswith(timestamps.MAGIC))
        read_digest, root = timestamps.read_proof_file(proof)
        self.assertEqual(read_digest, digest)
        self.assertEqual([uri for _, uri in timestamps.pending_uris(root)], [CALENDAR])
        upgraded, changed = timestamps.upgrade(proof, transport)
        self.assertTrue(changed)
        self.assertEqual(timestamps.bitcoin_heights(timestamps.read_proof_file(upgraded)[1]), [860000])
        self.assertEqual(calls[0], ("POST", "/digest"))
        self.assertTrue(calls[1][1].startswith("/timestamp/"))
        # Serializing a parsed proof reproduces the same bytes.
        self.assertEqual(timestamps.proof_file(*timestamps.read_proof_file(upgraded)), upgraded)

    def test_untrusted_or_malformed_answers_are_ignored(self):
        transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"\x99garbage"))
        self.assertEqual(timestamps.submit(b"\x00" * 32, transport), (None, []))
        root = timestamps.Timestamp(b"\x01" * 32)
        payload = io.BytesIO()
        timestamps.write_varbytes(payload, b"https://evil.example/")
        root.attestations.append((timestamps.PENDING, payload.getvalue()))
        proof = timestamps.proof_file(b"\x01" * 32, root)
        def fail(request):
            raise AssertionError("No debe consultar calendarios no confiables.")
        self.assertEqual(timestamps.upgrade(proof, httpx.MockTransport(fail)), (proof, False))
        with self.assertRaises(timestamps.ProofError):
            timestamps.read_proof_file(b"not a proof")

    def test_certificate_stamp_pages_and_command_state(self):
        certificate = self.certificate()
        transport = httpx.MockTransport(lambda request: httpx.Response(200, content=pending_reply() if request.method == "POST" else bitcoin_reply(900001)))
        record = timestamps.stamp_certificate(certificate, transport)
        self.assertEqual(timestamps.read_proof_file(record.proof)[0], bytes.fromhex(certificate.fingerprint))
        self.assertEqual(timestamps.stamp_certificate(certificate, transport).pk, record.pk)
        detail = self.client.get(reverse("certificate-detail", args=[certificate.pk]))
        self.assertContains(detail, "Sello en Bitcoin")
        self.assertContains(detail, reverse("certificate-proof", args=[certificate.pk]))
        download = self.client.get(reverse("certificate-proof", args=[certificate.pk]))
        self.assertEqual(bytes(download.content), bytes(record.proof))
        self.assertEqual(self.client.get(reverse("certificate-public-proof", args=[certificate.pk])).status_code, 404)
        record = timestamps.upgrade_record(record, transport)
        self.assertEqual(record.bitcoin_height, 900001)
        self.client.post(reverse("certificate-share", args=[certificate.pk]), {"public": "yes"})
        self.client.logout()
        self.assertContains(self.client.get(reverse("certificate-verify", args=[certificate.pk])), "900001")
        self.assertEqual(self.client.get(reverse("certificate-public-proof", args=[certificate.pk])).status_code, 200)

    @override_settings(CERTIFICATE_TIMESTAMPS=False)
    def test_disabled_timestamps_never_contact_calendars(self):
        certificate = self.certificate()
        def fail(request):
            raise AssertionError("Sin red cuando el sello está desactivado.")
        self.assertIsNone(timestamps.stamp_certificate(certificate, httpx.MockTransport(fail)))
        self.assertFalse(CertificateTimestamp.objects.exists())


@override_settings(SECURE_SSL_REDIRECT=False)
class ReviewGalleryPathTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("creator@reviews.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Educadora", status="approved")
        self.admin = users.create_superuser("admin@reviews.invalid")
        self.student = users.create_user("student@reviews.invalid", display_name="Alias Público")
        self.other = users.create_user("other@reviews.invalid")
        self.course = Course.objects.create(creator=self.creator, title="Curso con reseñas", description="Descripción", status="published")
        chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        self.free = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Gratis", body="Texto", status="published")
        self.paid = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="De pago", body="Texto", access_type="paid", status="published", position=2)
        PracticeDraft.objects.create(lesson=self.free, title="Proyecto final", instructions="Construye algo", criteria=["Funciona"], review_days=3)
        self.version = publish_course(self.course, self.admin)
        self.records = list(self.version.chapters.first().lessons.order_by("position"))
        self.enrollment = enroll(self.student, self.version)
        self.client.force_login(self.student)

    def complete_all(self, student=None, enrollment=None):
        enrollment = enrollment or self.enrollment
        for revision, record in enumerate(self.records):
            save_progress(student or self.student, enrollment.pk, record.pk, revision, "complete")

    def test_only_buyers_or_finishers_review_once_and_creator_replies(self):
        self.assertEqual(review_basis(self.student, self.course), (None, None))
        with self.assertRaises(PermissionDenied):
            save_review(self.student, self.course, 5, "Muy bien")
        Entitlement.objects.create(buyer=self.student, resource=self.records[1].content)
        self.assertEqual(review_basis(self.student, self.course)[0], "purchase")
        save_review(self.student, self.course, 4, "  Claro y práctico  ")
        review = save_review(self.student, self.course, 5, "Mejor tras repasar")
        self.assertEqual((CourseReview.objects.count(), review.rating, review.body), (1, 5, "Mejor tras repasar"))
        with self.assertRaises(ValidationError):
            save_review(self.student, self.course, 6, "")
        with self.assertRaises(PermissionDenied):
            reply_review(self.other, review, "Gracias")
        reply_review(self.creator, review, "¡Gracias por tu reseña!")
        self.assertEqual(rating_summary(self.course), {"count": 1, "average": 5.0, "stars": 5})
        page = self.client.get(reverse("course-detail", args=[self.course.pk]))
        self.assertContains(page, "Alias Público")
        self.assertContains(page, "Compra verificada")
        self.assertContains(page, "¡Gracias por tu reseña!")
        CourseReview.objects.update(hidden=True)
        self.assertEqual(rating_summary(self.course)["count"], 0)

    def test_completed_course_review_through_the_page(self):
        other = enroll(self.other, self.version)
        Entitlement.objects.create(buyer=self.other, resource=self.records[1].content)
        self.complete_all(self.other, other)
        self.client.force_login(self.other)
        response = self.client.post(reverse("review-save", args=[self.course.pk]), {"rating": "3", "body": "Bien"})
        self.assertRedirects(response, reverse("course-version", args=[self.course.pk, self.version.number]) + "#course-reviews", fetch_redirect_response=False)
        self.assertEqual(CourseReview.objects.get().rating, 3)

    def test_gallery_shows_only_approved_shared_practices(self):
        practice = self.records[0].practice
        delivery = submit_delivery(self.student, practice.pk, "Mi solución pública", "https://example.org/demo", None, uuid.uuid4(), 0)
        with self.assertRaises(ValidationError):
            set_showcase(self.student, delivery.pk, True)
        review_delivery(self.creator, delivery.pk, "accepted", "Excelente", [0])
        with self.assertRaises(PermissionDenied):
            set_showcase(self.other, delivery.pk, True)
        self.assertEqual(gallery_items(self.course).count(), 0)
        self.client.post(reverse("showcase-toggle", args=[delivery.pk]), {"public": "yes"})
        self.assertEqual(gallery_items(self.course).count(), 1)
        self.client.logout()
        page = self.client.get(reverse("course-gallery", args=[self.course.pk]))
        self.assertContains(page, "Mi solución pública")
        self.assertContains(page, "Alias Público")
        self.client.force_login(self.student)
        self.client.post(reverse("showcase-toggle", args=[delivery.pk]), {"public": "no"})
        self.assertEqual(gallery_items(self.course).count(), 0)

    def test_path_progress_credential_and_public_verification(self):
        second = Course.objects.create(creator=self.creator, title="Segundo paso", description="Otro", status="published")
        chapter = Chapter.objects.create(course=second, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Única", body="Texto", status="published")
        second_version = publish_course(second, self.admin)
        path = LearningPath.objects.create(title="De cero a Lightning", slug="cero-lightning", summary="Ruta corta", published=True)
        PathCourse.objects.create(path=path, course=self.course, position=1)
        PathCourse.objects.create(path=path, course=second, position=2)
        self.assertContains(self.client.get(reverse("learning-paths")), "De cero a Lightning")
        Entitlement.objects.create(buyer=self.student, resource=self.records[1].content)
        self.complete_all()
        progress = path_progress(self.student, path)
        self.assertEqual((progress["finished"], progress["eligible"], progress["next"]["course"].pk), (1, False, second.pk))
        with self.assertRaises(ValidationError):
            issue_path_credential(self.student, path, "Lucía")
        second_enrollment = enroll(self.student, second_version)
        save_progress(self.student, second_enrollment.pk, second_version.chapters.first().lessons.first().pk, 0, "complete")
        response = self.client.post(reverse("learning-path", args=[path.slug]), {"student_name": "Lucía López"})
        completion = PathCompletion.objects.get()
        self.assertRedirects(response, reverse("path-credential", args=[completion.pk]))
        self.assertEqual(completion.fingerprint, path_digest(completion))
        self.assertEqual(len(completion.evidence), 2)
        self.assertEqual(issue_path_credential(self.student, path, "Otro").pk, completion.pk)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("path-verify", args=[completion.pk])).status_code, 404)
        self.client.force_login(self.student)
        self.client.post(reverse("path-credential", args=[completion.pk]), {"public": "yes"})
        self.client.logout()
        self.assertContains(self.client.get(reverse("path-verify", args=[completion.pk])), "coincide con el registro")
        data = self.client.get(reverse("path-verify-data", args=[completion.pk]))
        self.assertEqual(hashlib.sha256(data.content).hexdigest(), completion.fingerprint)
        completion.student_name = "Otra"
        with self.assertRaises(ValidationError):
            completion.save()
