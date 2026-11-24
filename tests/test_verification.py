"""Tests for community contributor and verification workflow engine."""

import pytest
from gojrilang.contributors import (
    Contributor,
    ContributorNotFoundError,
    get_contributor,
    list_contributors,
    register_contributor,
)
from gojrilang.verification import (
    VERIFICATION_STATUSES,
    AuditLogEntry,
    Submission,
    VerificationWorkflowError,
    get_audit_history,
    get_submission,
    list_submissions,
    review_submission,
    submit_entry,
)


def test_list_contributors():
    contribs = list_contributors()
    assert len(contribs) >= 2
    ids = {c.id for c in contribs}
    assert "CONTRIB_JKAACL_01" in ids
    assert "CONTRIB_CIIL_01" in ids


def test_get_contributor():
    c = get_contributor("CONTRIB_JKAACL_01")
    assert isinstance(c, Contributor)
    assert c.role == "reviewer"


def test_get_missing_contributor_raises():
    with pytest.raises(ContributorNotFoundError):
        get_contributor("NONEXISTENT_CONTRIB")


def test_register_contributor():
    new_c = Contributor(
        id="CONTRIB_TEST_USER",
        name="Test Community Scholar",
        role="contributor",
        affiliation="Gojri Folk Forum",
    )
    register_contributor(new_c)
    retrieved = get_contributor("CONTRIB_TEST_USER")
    assert retrieved.name == "Test Community Scholar"
    assert retrieved.role == "contributor"


def test_submit_entry():
    sub = submit_entry(
        item_type="word",
        data={
            "word": "ڈھوک",
            "word_roman": "ḍhok",
            "meaning_en": "highland summer pastoral settlement",
            "pos": "noun",
        },
        contributor_id="CONTRIB_COMMUNITY_01",
        source_citation="Oral consultation with pastoral elders",
    )
    assert isinstance(sub, Submission)
    assert sub.status == "community_submitted"
    assert sub.submission_id.startswith("SUB_")

    fetched = get_submission(sub.submission_id)
    assert fetched is not None
    assert fetched.submission_id == sub.submission_id


def test_5_stage_review_workflow():
    # 1. Submit
    sub = submit_entry(
        item_type="word",
        data={"word": "test_word", "meaning_en": "test meaning"},
        contributor_id="CONTRIB_COMMUNITY_01",
        source_citation="Field Note #42",
    )
    assert sub.status == "community_submitted"

    # 2. Advance to needs_review
    sub = review_submission(
        submission_id=sub.submission_id,
        reviewer_id="CONTRIB_JKAACL_01",
        new_status="needs_review",
        comments="Initial submission looks complete.",
    )
    assert sub.status == "needs_review"

    # 3. Advance to under_review
    sub = review_submission(
        submission_id=sub.submission_id,
        reviewer_id="CONTRIB_JKAACL_01",
        new_status="under_review",
        comments="Linguist currently verifying phonetics and cross-dialect usage.",
    )
    assert sub.status == "under_review"

    # 4. Advance to verified
    sub = review_submission(
        submission_id=sub.submission_id,
        reviewer_id="CONTRIB_JKAACL_01",
        new_status="verified",
        comments="Approved against JKAACL lexicographical records.",
    )
    assert sub.status == "verified"
    assert sub.reviewer_id == "CONTRIB_JKAACL_01"


def test_unauthorized_reviewer_cannot_verify():
    sub = submit_entry(
        item_type="word",
        data={"word": "unverified_word", "meaning_en": "meaning"},
        contributor_id="CONTRIB_COMMUNITY_01",
        source_citation="Unchecked web forum",
    )

    # Standard contributor cannot grant 'verified' status
    with pytest.raises(VerificationWorkflowError):
        review_submission(
            submission_id=sub.submission_id,
            reviewer_id="CONTRIB_COMMUNITY_01",  # role: contributor, not reviewer
            new_status="verified",
            comments="I approve my own word",
        )


def test_audit_history_logging():
    sub = submit_entry(
        item_type="proverb",
        data={"text": "نیکی کر تے باہک جا", "translation_en": "Do good and go to the meadow"},
        contributor_id="CONTRIB_COMMUNITY_01",
        source_citation="Oral Lore",
    )
    review_submission(
        submission_id=sub.submission_id,
        reviewer_id="CONTRIB_JKAACL_01",
        new_status="needs_review",
        comments="Logged check",
    )
    history = get_audit_history(sub.submission_id)
    assert len(history) >= 2  # Submission event + review event
    assert all(isinstance(h, AuditLogEntry) for h in history)
    assert history[0].action == "submitted"
    assert history[1].action == "transition_to_needs_review"
