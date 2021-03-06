# -*- coding: utf-8 -*-

from time import sleep

from pyrevit.coreutils import check_internet_connection
from pyrevit.coreutils.logger import get_logger
from pyrevit.coreutils.ribbon import ICON_LARGE
from pyrevit.loader.sessionmgr import load_session

import pyrevit.versionmgr.updater as updater
import pyrevit.versionmgr.upgrade as upgrade
from pyrevit.userconfig import user_config

from scriptutils import logger


__doc__ = 'Downloads updates from the remote libgit repositories (e.g github, bitbucket).'


def _check_connection():
    logger.info('Checking internet connection...')
    successful_url = check_internet_connection()
    if successful_url:
        logger.debug('Url access successful: {}'.format(successful_url))
        return True
    else:
        return False


def _check_for_updates():
    if _check_connection():
        logger.info('Checking for updates...')

        for repo in updater.get_all_extension_repos():
            if updater.has_pending_updates(repo):
                return True
    else:
        logger.warning('No internet access detected. Skipping check for updates.')
        return False


# noinspection PyUnusedLocal
def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    try:
        has_update_icon = script_cmp.get_bundle_file('icon_hasupdates.png')
        if user_config.core.checkupdates and _check_for_updates():
            ui_button_cmp.set_icon(has_update_icon, icon_size=ICON_LARGE)
    except:
        return


if __name__ == '__main__':
    # collect a list of all repos to be updates
    if _check_connection():
        repo_info_list = updater.get_all_extension_repos()
        logger.debug('List of repos to be updated: {}'.format(repo_info_list))

        for repo_info in repo_info_list:
            # update one by one
            logger.debug('Updating repo: {}'.format(repo_info.directory))
            try:
                upped_repo_info = updater.update_pyrevit(repo_info)
                logger.info(':inbox_tray: Successfully updated: {} to {}'.format(upped_repo_info.name,
                                                                                 upped_repo_info.last_commit_hash[:7]))
            except:
                logger.info('Can not update repo: {}  (Run in debug to see why)'.format(repo_info.name))

        # perform upgrade tasks
        logger.info('Upgrading settings...')
        upgrade.upgrade_existing_pyrevit()

        # now re-load pyrevit session.
        sleep(1)
        logger.info('Reloading...')
        load_session()
    else:
        logger.warning('No internet access detected. Skipping update.')
