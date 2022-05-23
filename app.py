from telethon import TelegramClient, sync, events
from telethon.errors import SessionPasswordNeededError
from config import API_ID, API_HASH
import re
import os

OUTPUT_CHANNEL = 'https://t.me/some_chat'

ERROR = "The specified message ID is invalid or you can't do that operation on such message (caused by ForwardMessagesRequest)"

LAST_MSG = None


def parse_file(filename: str):
    data = set()
    with open(filename, encoding='utf-8') as f:
        text = f.read().split('\n')
    for word in text:
        data.add(word.strip())
    return data


INPUT_CHANNELS = parse_file('channels.txt')


def main():
    client = TelegramClient('current-session', API_ID, API_HASH)
    if os.path.exists('current-session.session'):
        client.start()
    else:
        client = TelegramClient('current-session', API_ID, API_HASH)
        client.connect()

        phone = input("Enter phone: ")
        client.send_code_request(phone, force_sms=False)
        value = input("Enter login code: ")

        try:
            me = client.sign_in(phone, code=value)
        except SessionPasswordNeededError:
            password = input("Enter password: ")
            me = client.sign_in(password=password)

    @client.on(events.NewMessage(chats=INPUT_CHANNELS))
    async def normal_handler(event):
        global LAST_MSG
        keywords = parse_file('keywords.txt')
        for word in keywords:
            if re.search(rf'\b{word.lower()}\b', str(event.message).lower()):
                try:
                    if LAST_MSG != str(event.message):
                        await client.forward_messages(OUTPUT_CHANNEL, event.message)
                        LAST_MSG = str(event.message)
                        break
                except Exception as ex:
                    if ERROR not in str(ex):
                        await client.send_message(OUTPUT_CHANNEL, str(ex))

    client.run_until_disconnected()


if __name__ == '__main__':
    main()
