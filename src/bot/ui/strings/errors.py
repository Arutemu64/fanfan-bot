from environs import Env

env = Env()

user_not_found = "⚠️ Пользователь не найден!"
announce_too_fast = f"""⚠️ С прошлого анонса не прошло {env("ANNOUNCE_TIMEOUT")} секунд!
Чтобы избежать повторов, рассылка анонсов возможна раз в {env("ANNOUNCE_TIMEOUT")} секунд."""
access_denied = "⚠️ У вас нет доступа к этой команде!"
voting_disabled = "⚠️ Голосование сейчас отключено"
message_too_old = "⚠️ Этому сообщению больше 2 дней, удалите его вручную"
