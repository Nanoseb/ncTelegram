#!/usr/bin/env python3
"""
Configuration class to handle the settings
"""

import os
import sys
import subprocess
import psutil
import os.path
import configparser
import logging

logging.basicConfig(filename='logger.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO handle comand line argument:
# -c configfile
# --no-img to overwrite some parameters etc.

def load_config():
    """
    Tries to find a config file, reads it, and return the config as a dict
    """

    # Load config file following the rule "local path" → "home" → "/etc"
    confPriorityList = ['ncTelegram.conf',
            os.path.expanduser("~")+'/.ncTelegram.conf',
            '/etc/ncTelegram.conf']
    for conffile in confPriorityList:
        if os.path.isfile(conffile):
            break
    else:
        raise Exception("Configuration not found in {},"
              "please check your installation".format(confPriorityList))

    config = configparser.ConfigParser()
    config.read(conffile)

    config_full = {}

    config_full['general'] = {}
    config_full['style'] = {}
    config_full['keymap'] = {}

    # General settings
    settings = config['general']
    config_full['general']['phone_number'] = settings.get('phone_number', None)
    config_full['general']['user_login'] = settings.get('user_login', None)
    config_full['general']['notification'] = settings.getboolean('notification', True)
    config_full['general']['ninja_mode'] = settings.getboolean('ninja_mode', False)

    config_full['general']['inline_image'] = settings.getboolean('inline_image', True)
    config_full['general']['open_file'] = settings.getboolean('open_file', True)
    config_full['general']['date_format'] = settings.get('date_format', "%x", raw=True)

    # Style settings
    settings = config['style']
    config_full['style']['status_bar_fg'] = settings.get('status_bar_fg', 'bold, white')
    config_full['style']['status_bar_bg'] = settings.get('status_bar_bg', 'dark gray')
    config_full['style']['date'] = settings.get('date', 'light green')
    config_full['style']['hour'] = settings.get('hour', 'dark gray')
    config_full['style']['separator'] = settings.get('separator', 'dark gray')
    config_full['style']['cur_chan'] = settings.get('cur_chan', 'light green')
    config_full['style']['users_color'] = settings.get('users_color', 'dark red, '
                                                                      'dark green, '
                                                                      'brown, '
                                                                      'dark blue, '
                                                                      'dark magenta, '
                                                                      'dark cyan, '
                                                                      'light red, '
                                                                      'light green, '
                                                                      'yellow, '
                                                                      'light blue, '
                                                                      'light magenta, '
                                                                      'light cyan, '
                                                                      'white')
    config_full['style']['user_color'] = settings.get('user_color', 'light green')

    # Keymap settings
    settings = config['keymap']
    config_full['keymap']['left'] = settings.get('left', 'h')
    config_full['keymap']['right'] = settings.get('right', 'l')
    config_full['keymap']['up'] = settings.get('up', 'k')
    config_full['keymap']['down'] = settings.get('down', 'j')
    config_full['keymap']['quit'] = settings.get('quit', 'q')
    config_full['keymap']['insert_text'] = settings.get('insert_text', 'i')
    config_full['keymap']['open_file'] = settings.get('open_file', 'ctrl o')
    config_full['keymap']['line_break'] = settings.get('line_break', 'ctrl r')
    config_full['keymap']['next_chan'] = settings.get('next_chan', 'ctrl n')
    config_full['keymap']['prev_chan'] = settings.get('prev_chan', 'ctrl p')
    config_full['keymap']['hide_chanlist'] = settings.get('hide_chanlist', 'ctrl b')

    ##  Extra checks, disable configuration if features unavailable
    if not 'DISPLAY' in os.environ:
        logger.warning("'DISPLAY' not found, disabling graphical features")
        config_full['general']['notification'] = False
        config_full['general']['open_file'] = False

    if config_full['general']['notification']:
        try:
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify
        except Exception:
            logger.exception("Could not load gi, disabling notifications")
            config_full['general']['notification'] = False

    if config_full['general']['inline_image']:
        try:
            subprocess.call(['img2txt', '-h'],
                    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except Exception:
            logger.exception("Could not call img2text, disabling inline images")
            config_full['general']['inline_image'] = False

    return config_full

# vim: ai ts=4 sw=4 et sts=4
