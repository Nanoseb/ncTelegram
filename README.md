# ncTelegram
A curse Telegram client developed in Python with the urwid library.

![Presentation of ncTelegram](http://pix.toile-libre.org/upload/original/1457204711.png)

## Dependencies

* [Telegram-cli](https://github.com/vysheng/tg)
* [urwid](http://urwid.org)
* [pytg](https://github.com/luckydonald/pytg)
* libnotify (optional)
* caca-utils (optional)

## Installation

### For archlinux
You can use the pkgbuild from the aur repo

    yaourt -S nctelegram

### Other distribution

#### Telegram-cli
Just follow its [readme](https://github.com/vysheng/tg).

#### Urwid
This one should be in your repository

- Debian/ubuntu/...
```
    apt-get install python3-urwid 
```

- Fedora
```
    dnf install python-urwid
```
#### pytg

For now only pytg V0.4.5 is compatible with the stable branch of telegram-cli, so install it via: 
```
    pip install --user pytg==0.4.5
```

#### caca-utils and libnotify (optional)
These one should also be in your repos

- Debian/ubuntu/...
```
    apt-get install caca-utils libnotify
```

- Fedora
```
    dnf install caca-utils libnotify
```

### First launch

Before running `nctelegram` you have to launch `telegram-cli` in order to register you account (phone number and verification code).


## Usage

An example of configuration file can be found in `/etc/ncTelegram.conf`, copy it to your personal folder before modifying it : 
```
cp /etc/ncTelegram.conf ~/.ncTelegram.conf
```




