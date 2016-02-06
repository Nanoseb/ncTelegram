import urwid
import time

class MessageSendWidget(urwid.Filler):
    def __init__(self, Telegram_ui):
        self.Telegram_ui = Telegram_ui
        self.update_send_widget()


    def update_send_widget(self):
        self.update_status_bar()
        self.widgetEdit = urwid.Edit(" >> ", "", multiline=False)
        self.pile = urwid.Pile([self.attr, self.widgetEdit])
        super().__init__(self.pile)


    def update_status_bar(self):
        chan_name = self.Telegram_ui.current_chan['print_name'].replace('_',' ')
        chan_type = self.Telegram_ui.current_chan['type']
        if chan_type == 'chat':
            chan_num = self.Telegram_ui.current_chan['members_num']
            text = ' [ ' + chan_name + " ] --- [ " + str(chan_num) + " members ]"
        else:
            text = ' [ ' + chan_name + ' ]'

        self.status_bar = urwid.Text(('status_bar', text), align='left')
        self.attr = urwid.AttrMap(self.status_bar, 'status_bar')
        super().__init__(self.attr, 'top')


    def keypress(self, size, key):
        key = super(MessageSendWidget, self).keypress(size, key)
        if key == 'enter':
            msg = self.widgetEdit.get_edit_text()

            if msg == '/quit':
                self.Telegram_ui.exit()

            dst = self.Telegram_ui.current_chan['print_name']

            self.Telegram_ui.sender.send_msg(dst, msg)
            self.widgetEdit.set_edit_text("")

        # donner le focus a la liste
        if key == 'up' or key == 'page up':
            self.Telegram_ui.right_side.focus_position = 0

# vim: ai ts=4 sw=4 et sts=4
