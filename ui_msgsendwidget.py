import urwid
import time

class MessageSendWidget(urwid.Filler):
    def __init__(self, Telegram_ui):

        self.updateLocked = False
        self.Telegram_ui = Telegram_ui

        self.update_send_widget()

    def update_send_widget(self):
        self.widgetEdit = urwid.Edit(self.Telegram_ui.current_chan['print_name'].replace('_',' ') + " : ", "", multiline=False)
        super().__init__(self.widgetEdit)

    def keypress(self, size, key):
        key = super(MessageSendWidget, self).keypress(size, key)
        if key == 'enter':
            msg = self.widgetEdit.get_edit_text()

            if msg == '/quit':
                self.Telegram_ui.exit()

            dst = self.Telegram_ui.current_chan['print_name']

            self.Telegram_ui.sender.send_msg(dst, msg)
            self.widgetEdit.set_edit_text("")


# vim: ai ts=4 sw=4 et sts=4
