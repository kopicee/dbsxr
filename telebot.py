"""
Adapted from countera.py example in
https://github.com/nickoala/telepot/tree/master/examples
"""

import sys
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space


BOT_PREFIX = '!'

SUBSCRIBED_CHAT_ID = set()

class Idler(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def on_chat_message(self, msg):
        cid = self.chat_id

        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            return

        text = msg['text']
        if not text.startswith(BOT_PREFIX):
            return

        if msg['text'] != (BOT_PREFIX + 'sub'):
            return

        SUBSCRIBED_CHAT_ID.add(cid)
        await self.sender.sendMessage('Subscribed to updates')


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, Idler, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
