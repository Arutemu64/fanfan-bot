import enum


class PermissionObjectTypes(enum.StrEnum):
    MARKET = "market"


class Permissions(enum.StrEnum):
    CAN_MANAGE_SCHEDULE = "can_manage_schedule"
    CAN_CREATE_TICKETS = "can_create_tickets"
    CAN_VIEW_PARTICIPANTS = "can_view_participants"

    # Marketplace
    CAN_CREATE_MARKET = "can_create_market"
    CAN_MANAGE_MARKET = "can_manage_market"  # object_id is market_id
