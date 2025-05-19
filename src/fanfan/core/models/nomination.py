from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.vo.nomination import NominationId


@dataclass(slots=True, kw_only=True)
class Nomination:
    id: NominationId
    code: str
    title: str
    is_votable: bool
