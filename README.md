# ncTelegram
A curse Telegram client developed in Python with the urwid library.

<p align="center">
  <img src="http://pix.toile-libre.org/upload/original/1457204711.png" alt="screenshot of ncTelegram"/>
</p>


## Dependencies

* [Telegram-cli](https://github.com/vysheng/tg)
* [urwid](http://urwid.org)
* [pytg](https://github.com/luckydonald/pytg)
* libnotify (optional)
* caca-utils (optional)

## Installation

### For archlinux
You can use the pkgbuild from [aur](https://aur.archlinux.org/packages/nctelegram-git/):
```
$ yaourt -S nctelegram-git
```

### For Fedora
Everything is in the repos:

```
# dnf install telegram-cli python-urwid
```

If you want notifications and inline images:
```
# dnf install libnotify caca-utils
```

And ncTelegram:
```
# pip3 install --upgrade https://github.com/Nanoseb/ncTelegram/archive/0.9.2.tar.gz
```

### For Debian/ubuntu/...

To install telegram-cli just follow its [readme](https://github.com/vysheng/tg).

And then:
```
# apt-get install python3-urwid 
```

And if you want notifications and inline images:
```
# apt-get install libnotify caca-utils
```

Finnaly ncTelegram:
```
# pip3 install --upgrade https://github.com/Nanoseb/ncTelegram/archive/master.tar.gz
```

## Usage

Before running `nctelegram` you have to launch `telegram-cli` in order to register you account (phone number and verification code).

An example of configuration file can be found in `/etc/ncTelegram.conf`, copy it to your personal folder before modifying it: 
```
$ cp /etc/ncTelegram.conf ~/.ncTelegram.conf
```
Be sure that the path of `telegram-cli` and the public key are set correctly.


#### Tips

- press `esc` to leave the text area

- press `q` to quit the ncTelegram

- press `esc` twice to draw a separator at the end of the message list

- use `ctrl+o` to open the last file sent to the current chan or url

- to send files you can simply drag and drop them into your terminal or send as a message their path between single quotes (')

- you can navigate in the chan list with `ctrl+p` and `ctrl+n`

- select `Download message buffer` to navigate more quickly between chan

- vim like keymap is also available, use `hjkl` to navigate between lists, use `i` to select the text area and `esc` to leave it


#### Troubleshooting

If `nctelegram` crashes, first report the issue with the backtrace ;), and before restarting it check if `telegram-cli` is still running, if so kill it first.
