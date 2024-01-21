from aiogram import Router


def setup_router() -> Router:
    from fanfan.presentation.tgbot.dialogs.menus import (
        helper,
        main,
        org,
        schedule,
        settings,
        user_manager,
        voting,
    )

    visitor_router = Router()
    visitor_router.include_router(main.dialog)
    visitor_router.include_router(schedule.dialog)
    visitor_router.include_router(voting.dialog)
    visitor_router.include_router(settings.dialog)

    helper_router = Router()
    helper_router.include_router(helper.dialog)
    helper_router.include_router(user_manager.dialog)

    org_router = Router()
    org_router.include_router(org.dialog)

    dialog_router = Router()
    dialog_router.include_router(visitor_router)
    dialog_router.include_router(helper_router)
    dialog_router.include_router(org_router)

    return dialog_router
