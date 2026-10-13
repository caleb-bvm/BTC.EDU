"""Public teaching identity, independent from the account's private name."""


def public_creator_name(creator):
    profile = getattr(creator, "creator_profile", None)
    if profile:
        return profile.display_name if profile.status == "approved" else "Creador de BTC.EDU"
    # Preserve credits for legacy publications without an editorial profile.
    return creator.get_full_name().strip() or "Creador de BTC.EDU"
