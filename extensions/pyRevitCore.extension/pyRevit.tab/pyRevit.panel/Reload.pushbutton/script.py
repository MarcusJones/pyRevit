"""Searches the script folders and create buttons for the new script or newly installed extensions."""

from scriptutils import logger
from pyrevit.loader.sessionmgr import load_session

# re-load pyrevit session.
logger.info('Reloading....')
load_session()
