from dataclasses import dataclass


@dataclass
class BlockDTO:
    id: int
    title: str
    start_order: int
