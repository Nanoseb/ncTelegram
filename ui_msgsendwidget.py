import urwid


class MessageSendWidget(urwid.Filler):
    def __init__(self, Telegram_ui):

        self.updateLocked = False
        self.Telegram_ui = Telegram_ui
        
        #self.widgetEdit = urwid.Edit(Telegram_ui.current_chan + " : ", "", multiline=False)
        #super().__init__(self.widgetEdit)

        self.update_send_widget()

    def update_send_widget(self):
        self.widgetEdit = urwid.Edit(self.Telegram_ui.current_chan + " : ", "", multiline=False)
        super().__init__(self.widgetEdit)

    def keypress(self, size, key):
        key = super(MessageSendWidget, self).keypress(size, key)
        if key == 'enter':
            msg = self.widgetEdit.get_edit_text()
            dst = self.Telegram_ui.current_chan 

            self.Telegram_ui.sender.send_msg(dst, msg)
            
            self.widgetEdit.set_edit_text("")



