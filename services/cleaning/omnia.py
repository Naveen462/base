from .abstract import CleaningModule


class OmniaCleaningModule(CleaningModule):
    def __init__(self, config_ini, logger):
        CleaningModule.__init__(self, config_ini, logger)
