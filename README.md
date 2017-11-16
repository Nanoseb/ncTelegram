# ncTelegram

A ncurses Telegram client developed in Python with the urwid library.

<p align="center">
  <img src="http://pix.toile-libre.org/upload/original/1457204711.png" alt="screenshot of ncTelegram"/>
</p>

## Dependencies

* [Telegram-cli](https://github.com/vysheng/tg)
* [urwid](http://urwid.org)
* [pytg](https://github.com/luckydonald/pytg)
* python-psutil
* libnotify (optional)
* caca-utils (optional)

## Installation

### Arch Linux:

You can use the pkgbuild from [AUR](https://aur.archlinux.org/packages/nctelegram-git/):

```
$ yaourt -S nctelegram-git

OR

$ pacaur -y nctelegram-git
```

### Fedora:

Install dependencies:

```
$ sudo dnf install telegram-cli python3-urwid python3-psutil python3-pip
```

Install ncTelegram through pip:
```
$ sudo pip3 install --upgrade https://github.com/Nanoseb/ncTelegram/archive/master.tar.gz
```

If you want notifications and inline images:

```
$ sudo dnf install libnotify caca-utils
```

### Debian/Ubuntu:

To install telegram-cli just follow its [readme](https://github.com/vysheng/tg).

Install urwid:

```
$ sudo apt-get install python3-urwid python3-psutil python3-pip
```

Install ncTelegram through pip:

```
$ sudo pip3 install --upgrade https://github.com/Nanoseb/ncTelegram/archive/master.tar.gz
```

If you want notifications and inline images:

```
$ sudo apt-get install libnotify-bin caca-utils
```

### Crux:

Install repository:

```
$ wget -O /etc/ports/wildefyr.httpup "https://crux.nu/portdb/?a=getup&q=wildefyr"
$ ports -u
```

Install ncTelegram:

```
$ prt-get depinst nctelegram
```

If you want notifications and inline images:

```
$ prt-get depinst libnotify libcaca
```

## Usage

Before the first run of `nctelegram`, `telegram-cli` must be launched first in
order to register your account on your machine for the first time. (phone number
and verification code).

An example of the configuration file can be found in `/etc/ncTelegram.conf`,
copy it to your personal folder before modifying it:

```
$ cp /etc/ncTelegram.conf ~/.ncTelegram.conf
```

Finally, make sure that the path of `telegram-cli` and the public key are set
correctly in `~/.ncTelegram.conf`.

#### Tips

- Press `esc` to leave the text area.

- Press `q` to quit the ncTelegram.

- Press `esc` twice to draw a separator at the end of the message list.

- Use `ctrl+o` to open the last file or url sent to the current channel.

- Use `ctrl+r` to insert a linebreak.

- To send files you can simply drag and drop them into your terminal or send as
a message their path between single quotes (').

- You can navigate the channel list with `ctrl+p` and `ctrl+n`.

- Select `Download message buffer` to navigate quickly between channels.

- Vim-like key bindings are also available, use `hjkl` to navigate between
lists, use `i` to select the text area and `esc` to leave it.

- You can also use `ctrl+w` to remove words left of the cursor and `ctrl+u` to remove the whole line.

- Use `shift + Up` or `shift + Down` to navigate in your own message history.

#### Troubleshooting

If `nctelegram` crashes, please [report the
issue](https://github.com/Nanoseb/ncTelegram/issues/new) with a backtrace if
possible.

Before restarting `nctelegram` again, check if `telegram-cli` is
still running; if so kill it before restarting `nctelegram`.
