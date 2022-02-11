from datetime import datetime
import os
import os.path as path

def get_timestamp(dt=None, fmt="%Y-%m-%d-%H%M"):
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

