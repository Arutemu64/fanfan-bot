import enum


class PermissionObjectTypes(enum.StrEnum):
    MARKET = "market"


class Permissions(enum.StrEnum):
    CAN_EDIT_SCHEDULE = "can_edit_schedule"
    CAN_CREATE_TICKETS = "can_create_tickets"
    CAN_MANAGE_MARKET = "can_manage_market"  # object_id is market_id
