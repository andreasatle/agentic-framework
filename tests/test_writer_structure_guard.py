from __future__ import annotations

import pytest

from domain.writer.main import main as writer_main
from domain.writer.schemas import WriterDomainState


def test_writer_raises_without_structure(monkeypatch):
    def fake_load_state(topic=None):
        return WriterDomainState()

    def fake_save_state(self, topic=None):
        return None

    monkeypatch.setattr("domain.writer.schemas.WriterDomainState.load", staticmethod(fake_load_state))
    monkeypatch.setattr("domain.writer.schemas.WriterDomainState.save", fake_save_state)

    with pytest.raises(RuntimeError):
        writer_main()
