import re

from telethon import TelegramClient, events

from config import API_ID, API_HASH

OUTPUT_CHANNEL = -100000000000

ERROR = "The specified message ID is invalid or you can't do that operation on such message (caused by ForwardMessagesRequest)"


def skipper(data: set, message: str):
    for word in data:
        if word in message.lower():
            return False
    return True


def parse_file(filename: str):
    with open(filename, encoding='utf-8') as f:
        text = f.read().split('\n')
    data = set(word.strip().lower() for word in text)
    return data


def parse_channels(filename: str):
    data = set()
    with open(filename, encoding='utf-8') as f:
        text = f.read().split('\n')
    for word in text:
        try:
            data.add(int(word.strip()))
        except ValueError:
            data.add(word.strip())
    return data


def main():
    INPUT_CHANNELS = parse_channels('channels.txt')
    KEYWORDS = parse_file('keywords.txt')
    FALSE_POS = parse_file('false_pos.txt')

    client = TelegramClient('current-session', API_ID, API_HASH)
    client.start()

    @client.on(events.NewMessage(chats=INPUT_CHANNELS))
    async def normal_handler(event):
        if skipper(FALSE_POS, str(event.message.message)):
            for word in KEYWORDS:
                if re.search(rf'\b{str(word)}\b', str(event.message.message).lower()):
                    try:
                        await client.forward_messages(await client.get_entity(OUTPUT_CHANNEL), event.message)
                        break

                    except Exception as ex:
                        if ERROR not in str(ex):
                            await client.send_message(await client.get_entity(OUTPUT_CHANNEL), str(ex))

    client.run_until_disconnected()


if __name__ == '__main__':
    main()
