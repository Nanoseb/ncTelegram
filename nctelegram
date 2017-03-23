#!/usr/bin/env python3
import os
import sys
import subprocess
import psutil
import os.path
import configparser

import ncTelegram



for connection in psutil.net_connections():
    if connection[4] and connection[4][1] == 4458:
        print('WARNING: telegram-cli seems to be already running, if you experience connection issues make sure you kill it before restarting ncTelegram')
#         sys.exit(1)


confPriorityList = ['ncTelegram.conf', os.path.expanduser("~")+'/.ncTelegram.conf', '/etc/ncTelegram.conf']
for conffile in confPriorityList:
    if os.path.isfile(conffile):
        break

config = configparser.ConfigParser()
config.read(conffile)

config_full = {}

config_full['general'] = {}
config_full['style'] = {}
config_full['keymap'] = {}

config_full['general']['path_telegram'] = config['general'].get('path_telegram', "/usr/bin/telegram-cli")
config_full['general']['path_pubkey'] = config['general'].get('path_pubkey', "/etc/telegram-cli/server.pub")
config_full['general']['notification'] = config['general'].getboolean('notification', True)
config_full['general']['ninja_mode'] = config['general'].getboolean('ninja_mode', False)

config_full['general']['inline_image'] = config['general'].getboolean('inline_image', True)
config_full['general']['open_file'] = config['general'].getboolean('open_file', True)
config_full['general']['date_format'] = config['general'].get('date_format', "%x", raw=True)

config_full['style']['status_bar_fg'] = config['style'].get('status_bar_fg', 'bold, white')
config_full['style']['status_bar_bg'] = config['style'].get('status_bar_bg', 'dark gray')
config_full['style']['date'] = config['style'].get('date', 'light green')
config_full['style']['hour'] = config['style'].get('hour', 'dark gray')
config_full['style']['separator'] = config['style'].get('separator', 'dark gray')
config_full['style']['cur_chan'] = config['style'].get('cur_chan', 'light green')
config_full['style']['users_color'] = config['style'].get('users_color', 'dark red, '
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
config_full['style']['user_color'] = config['style'].get('user_color', 'light green')

config_full['keymap']['left'] = config['keymap'].get('left', 'h')
config_full['keymap']['right'] = config['keymap'].get('right', 'l')
config_full['keymap']['up'] = config['keymap'].get('up', 'k')
config_full['keymap']['down'] = config['keymap'].get('down', 'j')
config_full['keymap']['quit'] = config['keymap'].get('quit', 'q')
config_full['keymap']['insert_text'] = config['keymap'].get('insert_text', 'i')
config_full['keymap']['open_file'] = config['keymap'].get('open_file', 'ctrl o')
config_full['keymap']['line_break'] = config['keymap'].get('line_break', 'ctrl r')
config_full['keymap']['next_chan'] = config['keymap'].get('next_chan', 'ctrl n')
config_full['keymap']['prev_chan'] = config['keymap'].get('prev_chan', 'ctrl p')
config_full['keymap']['hide_chanlist'] = config['keymap'].get('hide_chanlist', 'ctrl b')

if not 'DISPLAY' in os.environ:
    config_full['general']['notification'] = False
    config_full['general']['open_file'] = False

if config_full['general']['notification']:
    try:
        import gi
        gi.require_version('Notify', '0.7')
        from gi.repository import Notify
    except:
        config_full['general']['notification'] = False

if config_full['general']['inline_image']:
    try:
        subprocess.call(['img2txt', '-h'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except:
        config_full['general']['inline_image'] = False

ncTelegram.Telegram_ui(config_full)



# vim: ai ts=4 sw=4 et sts=4
