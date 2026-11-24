"""Community submission and multi-stage verification workflow engine for GojriLang.

Implements the five-stage verification lifecycle:
1. community_submitted
2. needs_review
3. under_review
4. verified
5. rejected

Enforces reviewer authorization checks, provenance citations, and audit logging.
"""

from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set

from gojrilang.contributors import get_contributor
from gojrilang.exceptions import GojriLangError


class VerificationWorkflowError(GojriLangError):
    """Raised when a verification workflow constraint or permission check fails."""
    pass


VERIFICATION_STATUSES: Set[str] = {
    "community_submitted",
    "needs_review",
    "under_review",
    "verified",
    "rejected",
}


@dataclass
class AuditLogEntry:
    """An immutable record of a modification or verification transition."""

    log_id: str
    submission_id: str
    action: str  # submitted, moved_to_review, verified, rejected, updated
    actor_id: str
    previous_status: Optional[str]
    new_status: str
    comments: Optional[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Submission:
    """A community submitted linguistic record, word, translation, song, or proverb."""

    submission_id: str
    item_type: str  # word, translation, song, proverb, folklore, correction
    data: Dict[str, Any]
    contributor_id: str
    source_citation: str
    status: str = "community_submitted"
    reviewer_id: Optional[str] = None
    reviewer_comments: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_SUBMISSIONS_REGISTRY: Dict[str, Submission] = {}
_AUDIT_LOG: List[AuditLogEntry] = []
_SUBMISSION_COUNTER = 1000
_LOG_COUNTER = 5000


def submit_entry(
    item_type: str,
    data: Dict[str, Any],
    contributor_id: str,
    source_citation: str,
) -> Submission:
    """Submit a new linguistic or cultural item for community review.

    Args:
        item_type: Category ('word', 'translation', 'song', 'proverb', 'folklore', 'correction').
        data: Record dictionary containing text, meanings, dialect, etc.
        contributor_id: Registered contributor ID.
        source_citation: Reference, field consultant, or bibliographic citation.

    Returns:
        The newly created Submission record in 'community_submitted' status.
    """
    global _SUBMISSION_COUNTER, _LOG_COUNTER
    if not source_citation or not source_citation.strip():
        raise VerificationWorkflowError("Submissions require a non-empty source_citation for provenance.")

    # Validate contributor exists
    get_contributor(contributor_id)

    _SUBMISSION_COUNTER += 1
    sub_id = f"SUB_{_SUBMISSION_COUNTER}"
    now_str = datetime.datetime.now().isoformat()

    sub = Submission(
        submission_id=sub_id,
        item_type=item_type.strip().lower(),
        data=data,
        contributor_id=contributor_id,
        source_citation=source_citation.strip(),
        status="community_submitted",
        created_at=now_str,
        updated_at=now_str,
    )
    _SUBMISSIONS_REGISTRY[sub_id] = sub

    _LOG_COUNTER += 1
    log_entry = AuditLogEntry(
        log_id=f"LOG_{_LOG_COUNTER}",
        submission_id=sub_id,
        action="submitted",
        actor_id=contributor_id,
        previous_status=None,
        new_status="community_submitted",
        comments=f"New {item_type} submitted with citation: {source_citation}",
        timestamp=now_str,
    )
    _AUDIT_LOG.append(log_entry)
    return sub


def review_submission(
    submission_id: str,
    reviewer_id: str,
    new_status: str,
    comments: Optional[str] = None,
) -> Submission:
    """Review and transition a submission's verification status.

    Only authorized reviewers (role 'reviewer', 'linguist', or 'administrator')
    may mark a submission as 'verified' or 'rejected'.
    """
    global _LOG_COUNTER
    sub = _SUBMISSIONS_REGISTRY.get(submission_id.strip())
    if not sub:
        raise VerificationWorkflowError(f"Submission '{submission_id}' was not found.")

    status_clean = new_status.strip().lower()
    if status_clean not in VERIFICATION_STATUSES:
        raise VerificationWorkflowError(
            f"Invalid verification status '{new_status}'. Allowed: {sorted(list(VERIFICATION_STATUSES))}"
        )

    # Permission check for privileged transitions
    reviewer = get_contributor(reviewer_id)
    if status_clean in ("verified", "rejected") and reviewer.role not in ("reviewer", "linguist", "administrator"):
        raise VerificationWorkflowError(
            f"Contributor '{reviewer_id}' has role '{reviewer.role}' and lacks authority to set status to '{status_clean}'."
        )

    old_status = sub.status
    now_str = datetime.datetime.now().isoformat()
    sub.status = status_clean
    sub.reviewer_id = reviewer_id
    sub.reviewer_comments = comments
    sub.updated_at = now_str

    _LOG_COUNTER += 1
    log_entry = AuditLogEntry(
        log_id=f"LOG_{_LOG_COUNTER}",
        submission_id=sub.submission_id,
        action=f"transition_to_{status_clean}",
        actor_id=reviewer_id,
        previous_status=old_status,
        new_status=status_clean,
        comments=comments,
        timestamp=now_str,
    )
    _AUDIT_LOG.append(log_entry)
    return sub


def get_submission(submission_id: str) -> Optional[Submission]:
    """Retrieve a submission record by ID."""
    return _SUBMISSIONS_REGISTRY.get(submission_id.strip())


def list_submissions(
    status: Optional[str] = None,
    item_type: Optional[str] = None,
) -> List[Submission]:
    """List submissions filtered by verification status or item type."""
    results = []
    for sub in _SUBMISSIONS_REGISTRY.values():
        if status and sub.status.lower() != status.strip().lower():
            continue
        if item_type and sub.item_type.lower() != item_type.strip().lower():
            continue
        results.append(sub)
    return results


def get_audit_history(submission_id: Optional[str] = None) -> List[AuditLogEntry]:
    """Return audit log entries, optionally filtered by submission ID."""
    if submission_id:
        clean_id = submission_id.strip()
        return [l for l in _AUDIT_LOG if l.submission_id == clean_id]
    return list(_AUDIT_LOG)
