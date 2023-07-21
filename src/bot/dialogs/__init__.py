from aiogram import Router

from src.bot.filters import RoleFilter


def setup_router() -> Router:
    from src.bot.dialogs import announce_mode, helper, main, org, registration, voting

    registration_router = Router()
    registration_router.include_router(registration.dialog)

    common_router = Router()
    common_router.message.filter(RoleFilter(["visitor", "helper", "org"]))
    common_router.include_router(main.dialog)
    common_router.include_router(voting.dialog)

    helper_router = Router()
    helper_router.callback_query.filter(RoleFilter(["helper", "org"]))
    helper_router.include_router(helper.dialog)
    helper_router.include_router(announce_mode.dialog)

    org_router = Router()
    org_router.callback_query.filter(RoleFilter(["org"]))
    org_router.include_router(org.dialog)

    dialog_router = Router()
    dialog_router.include_router(registration_router)
    dialog_router.include_router(common_router)
    dialog_router.include_router(helper_router)
    dialog_router.include_router(org_router)

    return dialog_router
