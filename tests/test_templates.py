"""The vault templates and the hook that fills them must agree.

`scripts/brain-session-end.py` writes the daily-log stub by substituting
placeholders in `knowledge/templates/daily-log.md`. The hook lives outside the
package, so pytest cannot import it — but both are text, and the pair only
breaks in one way: a placeholder in the template that the hook does not
substitute, or a literal date frozen into the template instead of one. That is
exactly the bug this test was written after, where every stub carried
2026-07-26.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = REPO_ROOT / "knowledge" / "templates" / "daily-log.md"
HOOK = REPO_ROOT / "scripts" / "brain-session-end.py"
PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def test_every_template_placeholder_is_substituted_by_the_hook():
    template = TEMPLATE.read_text(encoding="utf-8")
    hook = HOOK.read_text(encoding="utf-8")
    unhandled = [name for name in PLACEHOLDER.findall(template) if f'"{{{{{name}}}}}"' not in hook]
    assert not unhandled, f"the hook never substitutes {unhandled}"


def test_the_daily_log_template_has_no_frozen_date():
    template = TEMPLATE.read_text(encoding="utf-8")
    assert "{{DATE}}" in template, "the template must ask for a date"
    assert not ISO_DATE.search(template), "a literal date here stamps every stub with it"
