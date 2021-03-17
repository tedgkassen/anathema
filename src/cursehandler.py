from handler import Handler
from curse import CurseManager


class CurseHandler(Handler):
    def __init__(self, c: CurseManager):
        self.c = c

    async def process(self, message):
        if message.content.sptrip() == '!are-we-cursed':
            await message.channel.send(self.get_curse_query_response())
        elif message.content.strip() == '!lift-curse':
            await message.channel.send(self.reset_response())

    def get_curse_query_response(self):
        cursedness = self.c.get_cursedness()

        if not cursedness:
            return "There is not enough information to determine if you are cursed."

        if cursedness < .1:
            message = "The gods smile up on you."
        elif cursedness < .25:
            message = "You are blessed."
        elif cursedness < .4:
            message = "You have nothing to complain about."
        elif cursedness < .6:
            message = "Your dice work as intended."
        elif cursedness < .75:
            message = "You are fairly cursed."
        else:
            message = "Y'all are absolutely fucked"

        return "Cursedness level is {}` : {}".format(cursedness, message)

    def reset_response(self):
        self.c.purify()
        return "The curse has been lifted."
