from fanfan.core.exceptions.base import AppException


class SettingsException(AppException):
    pass


class SettingsNotFound(SettingsException):
    pass
