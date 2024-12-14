from dataclasses import dataclass
from typing import NewType

BlockId = NewType("BlockId", int)


@dataclass(slots=True, kw_only=True)
class Block:
    id: BlockId
    title: str
