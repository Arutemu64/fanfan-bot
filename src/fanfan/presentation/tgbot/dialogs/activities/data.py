from dataclasses import dataclass

from fanfan.core.vo.activity import ActivityId


@dataclass(slots=True)
class ActivitiesDialogData:
    activity_id: ActivityId
