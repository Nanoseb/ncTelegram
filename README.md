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
You can use the pkgbuild from [aur](https://aur.archlinux.org/packages/nctelegram-git/)
```
yaourt -S nctelegram-git
```
And install pytg with pip:

```
pip install --user pytg==0.4.5
```

### Other distributions

#### Telegram-cli
Just follow its [readme](https://github.com/vysheng/tg).

#### Urwid
This one should be in your repository

- On Debian/ubuntu/...
```
    apt-get install python3-urwid 
```

- On Fedora
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

- On Debian/ubuntu/...
```
    apt-get install caca-utils libnotify
```

- On Fedora
```
    dnf install caca-utils libnotify
```

### Installation of ncTelegram

```
git clone https://github.com/Nanoseb/ncTelegram.git
cd ncTelegram
python3 setup.py install
```

Before running `nctelegram` you have to launch `telegram-cli` in order to register you account (phone number and verification code).


## Usage

An example of configuration file can be found in `/etc/ncTelegram.conf`, copy it to your personal folder before modifying it : 
```
cp /etc/ncTelegram.conf ~/.ncTelegram.conf
```
Be sure that the path of `telegram-cli` and the public key in the configuration file are correct.




