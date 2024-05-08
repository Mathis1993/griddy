class SmartthingsApiException(Exception):
    pass


class CommandModuleException(Exception):
    def __str__(self):
        return "Provide the 'module' kwarg to know for which component a command should be executed"
