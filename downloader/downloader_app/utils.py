"""
from downloader_app.ci.config import EE_CREDENTIAL_FILE, EE_SERVICE_ACCOUNT


def ee_authenticate():
    if not os.path.exists(EE_CREDENTIAL_FILE):
        raise Exception("CREADENTIAL FILE DOESN'T EXIST")
    credentials = ee.ServiceAccountCredentials(
        EE_SERVICE_ACCOUNT, EE_CREDENTIAL_FILE
    )
    ee.Initialize(credentials)
"""
