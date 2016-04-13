#!/usr/bin/env python

from distutils.core import setup

setup(name='ncTelegram',
      version='0.9.5',
      description='A curse Telegram client',
      license='GPLv3',
      author='Sébastien Lemaire',
      url='https://github.com/Nanoseb/ncTelegram',
      packages=['ncTelegram'],
      scripts=['nctelegram'],
      data_files=[('/etc', ['ncTelegram.conf']),
                  ('/usr/share/ncTelegram', ['t_logo.png']),],
      install_requires=["pytg>=0.4.10"]

      )
