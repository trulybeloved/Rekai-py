from appconfig import AppConfig
from db_management import SystemDBM, JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM, GeminiGPTDBM

def rekai_initialize():

    sys_dbm = SystemDBM(mode=0)
    sys_dbm.check_and_initialize()

    database_managers = [JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM, GeminiGPTDBM]
    for dbm in database_managers:
        dbm = dbm()
        dbm.check_and_initialize()
