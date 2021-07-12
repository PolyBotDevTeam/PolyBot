class Action:

    def __init__(self):
        pass


class Message(Action):

    def __init__(self, *, text='', attachments=(), disable_mentions=False):
        self.__text = text
        self.__attachments = tuple(attachments)
        self.__disable_mentions = disable_mentions

    @property
    def text(self):
        return self.__text

    @property
    def attachments(self):
        return self.__attachments

    @property
    def disable_mentions(self):
        return self.__disable_mentions
