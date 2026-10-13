"""The reader and course community share the same lesson-scoped threads."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q
from django.urls import reverse

from .community import access, accessible_posts, post_message
from .essential_forms import MessageForm
from .models import CommunitySubscription


def lesson_url(version, lesson_id):
    return reverse("version-lesson", args=[version.course_id, version.number, lesson_id])


def conversation_url(actor, post):
    root = post.parent if post.parent_id else post
    posts = accessible_posts(actor, post.version).filter(lesson_id=post.lesson_id, parent__isnull=True)
    from .community import moderator
    if not moderator(actor, post.version):
        posts = posts.filter(hidden=False)
    page = posts.filter(Q(created_at__gt=root.created_at) | Q(created_at=root.created_at, pk__gt=root.pk)).count() // 5 + 1
    return lesson_url(post.version, post.lesson_id) + f"?conversaciones={page}#conversation-{root.pk}"


def submit(request, version, lesson):
    access(request.user, version, writing=True)
    parent_id = request.POST.get("parent", "")
    try:
        parent_id = int(parent_id) if parent_id else None
    except ValueError:
        raise PermissionDenied
    form = MessageForm(request.POST, auto_id=f"lesson-reply-{parent_id}-%s" if parent_id else "lesson-comment-%s")
    post = None
    if form.is_valid():
        try:
            post = post_message(request.user, version, form.cleaned_data["body"], form.cleaned_data["request_key"], parent_id, lesson.pk)
        except ValidationError as exc:
            form.add_error(None, exc)
    return post, form, parent_id


def reader_context(request, version, lesson, submitted_form=None, submitted_parent=None):
    url = lesson_url(version, lesson.pk)
    data = {"discussion_lesson_id": lesson.pk, "discussion_url": url, "discussion_available": False}
    try:
        access(request.user, version)
    except PermissionDenied:
        return data
    from .community_views import context
    permissions = context(request, version)
    posts = accessible_posts(request.user, version).filter(lesson=lesson, parent__isnull=True).select_related("author__creator_profile")
    if not permissions["can_moderate"]:
        posts = posts.filter(hidden=False)
    posts = posts.annotate(is_following=Exists(CommunitySubscription.objects.filter(thread_id=OuterRef("pk"), user=request.user))).order_by("-created_at", "-pk")
    page_number = request.GET.get("conversaciones")
    root = posts.filter(pk=submitted_parent).first() if submitted_parent else None
    if root:
        page_number = posts.filter(Q(created_at__gt=root.created_at) | Q(created_at=root.created_at, pk__gt=root.pk)).count() // 5 + 1
    page = Paginator(posts, 5).get_page(page_number)
    for post in page:
        replies = post.replies.select_related("author__creator_profile")
        if not permissions["can_moderate"]:
            replies = replies.filter(hidden=False)
        post.visible_reply_count = replies.count()
        post.reader_replies = list(reversed(list(replies.order_by("-created_at", "-pk")[:3])))
        post.reply_form = submitted_form if submitted_parent == post.pk else MessageForm(auto_id=f"lesson-reply-{post.pk}-%s")
    # A forged or stale parent must still show the error and preserve the text.
    parent_on_page = submitted_parent is not None and any(post.pk == submitted_parent and not post.closed and not post.hidden for post in page)
    data.update(
        discussion_available=True, discussion_can_write=permissions["can_write"], discussion_can_moderate=permissions["can_moderate"],
        discussion_suspended=permissions["suspended"],
        discussion_posts=page, discussion_form=submitted_form if submitted_form is not None and not parent_on_page else MessageForm(auto_id="lesson-comment-%s"),
        discussion_submitted_parent=submitted_parent if not parent_on_page else None,
    )
    return data
