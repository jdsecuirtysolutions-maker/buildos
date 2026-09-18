"""Deliberately faulty evaluation fixture, not production code."""


def can_read(actor, document):
    return actor.get("role") == "member"
