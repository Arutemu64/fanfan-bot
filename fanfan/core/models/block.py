from dataclasses import dataclass
from typing import NewType

BlockId = NewType("BlockId", int)


@dataclass(slots=True)
class BlockModel:
    id: BlockId
    title: str
