from telethon import TelegramClient, sync, events
from telethon.errors import SessionPasswordNeededError
from config import API_ID, API_HASH
import os

OUTPUT_CHANNEL = 'https://t.me/checker_forwarder_helper'


def parse_file(filename: str):
    data = []
    with open(filename, encoding='utf-8') as f:
        text = f.read().split('\n')
    for word in text:
        data.append(word.strip())
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
        keywords = parse_file('keywords.txt')
        for word in keywords:
            if word.lower() in str(event.message).lower():
                try:
                    await client.forward_messages(OUTPUT_CHANNEL, event.message)
                    break
                except Exception as ex:
                    await client.send_message(OUTPUT_CHANNEL, str(ex))
                    break

    client.run_until_disconnected()


if __name__ == '__main__':
    main()
