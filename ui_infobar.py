import urwid

# Une barre d'information statique
class InfoBar(urwid.Filler):
    # Constructeur usuel
    # text: le texte à afficher
    # style: le style à utiliser dans la palette
    # bar_align: l'alignement (vertical) de la barre
    # text_align: l'aligement (horizontal) du texte
    def __init__(self, text, style, bar_align, text_align):
        self.text = urwid.Text((style, text), align=text_align)
        self.attr = urwid.AttrMap(self.text, style)
        super().__init__(self.attr, bar_align)


# vim: ai ts=4 sw=4 et sts=4
