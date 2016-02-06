import urwid
import time

class MessageSendWidget(urwid.Filler):
    def __init__(self, Telegram_ui):
        self.Telegram_ui = Telegram_ui
        self.updateLockedauto = False
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

    def autocomplete(self):
        while (self.updateLockedauto):
            time.sleep(0.5)
        self.updateLockedauto = True

        type_chan = self.Telegram_ui.current_chan['type'] 
        print_name_chan = self.Telegram_ui.current_chan['print_name'] 

        username_list = []
        
        if type_chan == 'chat':        
            chat_info = self.Telegram_ui.sender.chat_info(print_name_chan)
            for user in chat_info['members']:
                if 'username' in user:
                    username_list.append(user['username'])

        elif type_chan == 'user' and 'username' in self.Telegram_ui.current_chan:
            username_list = [ self.Telegram_ui.current_chan['username'] ]
        
        elif type_chan == 'channel': 
            channel_info = self.Telegram_ui.sender.channel_info(print_name_chan)
            for user in channel_info['members']:
                if 'username' in user:
                    username_list.append(user['username'])


        text = self.widgetEdit.get_edit_text()[1:]

        self.updateLockedauto = False
        
        for user in username_list:
            if user.startswith(text):
                to_complete = user[len(text):]
                self.widgetEdit.insert_text(to_complete + ' ')
                break


    def keypress(self, size, key):
        key = super(MessageSendWidget, self).keypress(size, key)

        if key == 'enter':
            msg = self.widgetEdit.get_edit_text()

            if msg == '/quit':
                self.Telegram_ui.exit()

            dst = self.Telegram_ui.current_chan['print_name']

            self.Telegram_ui.sender.send_msg(dst, msg)
            self.widgetEdit.set_edit_text("")

        elif key == 'tab' and self.widgetEdit.get_edit_text().startswith("@") and \
                not ' ' in self.widgetEdit.get_edit_text():
            try:
                self.autocomplete()
            except:
                pass

        elif key == 'ctrl w' or key == 'ctrl k':
            self.widgetEdit.set_edit_text("")

        # donner le focus a la liste
        elif key == 'up' or key == 'page up' or key == 'esc':
            self.Telegram_ui.right_side.focus_position = 0

# vim: ai ts=4 sw=4 et sts=4
