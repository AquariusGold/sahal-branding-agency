# =============================================================================
# app/utils/device.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   SAHAL must deliver completely different UI experiences to mobile vs desktop
#   visitors — two separate template trees (templates/mobile/ & templates/desktop/).
#   Device detection must be centralised in ONE place so route handlers never
#   contain duplicated User-Agent parsing logic.
#
# HOW DEVICE DETECTION WORKS:
#   HTTP clients (browsers, apps) include a "User-Agent" header in every request.
#   Mobile browsers include identifiable keywords in that header string:
#     - "Mobile" appears in Android Chrome, iPhone Safari, etc.
#     - "Android" alone (without "Mobile") usually means a tablet; we treat it
#       as mobile too for a consistent experience.
#     - "iPhone", "iPad" (treated as mobile), "Windows Phone" are other signals.
#
#   We use a simple keyword-match approach rather than a third-party library
#   (like user-agents) to keep the dependency footprint minimal. If finer
#   granularity is needed later (tablet-specific UI, bot detection, etc.)
#   swap the implementation here without touching any route code.
#
# HOW IT INTEGRATES:
#   1. Routes import and call is_mobile(request) when selecting a template.
#   2. A context processor in create_app() injects `is_mobile` into every
#      Jinja2 template so templates can branch on device type if needed.
# =============================================================================

import re


# Keywords that reliably identify mobile browsers in the User-Agent string.
# The pattern is case-insensitive and checked against the full UA string.
_MOBILE_PATTERN = re.compile(
    r"(Mobile|Android|iPhone|iPad|Windows Phone|BlackBerry|Opera Mini|IEMobile)",
    re.IGNORECASE,
)


def is_mobile(request) -> bool:
    """
    Determine whether the incoming HTTP request originates from a mobile browser.

    Args:
        request: The Flask `request` proxy object (flask.request).

    Returns:
        True  — if the User-Agent string contains mobile-browser keywords.
        False — if the User-Agent is absent, unrecognised, or desktop-only.

    Usage in a route:
        from flask import request
        from app.utils.device import is_mobile

        @main.route("/")
        def index():
            template_prefix = "mobile" if is_mobile(request) else "desktop"
            return render_template(f"{template_prefix}/home.html")

    Usage inside a Jinja2 template (injected via context processor):
        {% if is_mobile %}
            <p>Mobile experience</p>
        {% else %}
            <p>Desktop experience</p>
        {% endif %}
    """

    # Safely fetch the User-Agent header.  If the header is missing (as in
    # some API-only clients or bots), default to empty string → desktop path.
    user_agent = request.headers.get("User-Agent", "")

    return bool(_MOBILE_PATTERN.search(user_agent))
