import json,sys
from slackbot import SlackBot

with open('oauthtoken.txt', 'r') as f:
    token = f.read().strip()
    f.close()

SYCSBot = SlackBot(token)

@SYCSBot.command('setup')
@SYCSBot.require_admin
def setup(message):
    command = message['text'][1:].split()
    if command[1].lower() == 'channel':
        with open('channels.json', 'r') as f:
            fc = json.loads(f.read())
            f.close()
        fc[command[2].lower()] = message['channel'].lower()
        with open('channels.json', 'w') as f:
            f.write(json.dumps(fc))
            f.close()
        response = '<@' + message['user'] + '> ' + 'Successfully set ' + command[2] + ' to channel <#' + message['channel'] + '>.'

    return response

@SYCSBot.command('stop')
@SYCSBot.require_admin
def stop(message):
    response = '<@' + message['user'] + '> ' + 'Stopping SYCS bot...'
    post_message(response, message['channel'])
    sys.exit()
    return ""

@SYCSBot.command('getchannel')
def getchannel(message):
    command = message['text'][1:].split()
    return '<@' + message['user'] + '> ' + get_channel(command[1]) or '<@' + message['user'] + '> ' + 'Channel not set up yet. Use !setup channel <channel name> in the channel to set it up.'

def get_channel(channel_name):
    with open('channels.json', 'r') as f:
        fc = json.loads(f.read())
        f.close()
    if channel_name in fc:
        return fc[channel_name].upper()
    return None


@SYCSBot.command('ping')
def ping(message):
    return f"PONG{message['ts']}"


@SYCSBot.command('admintest')
@SYCSBot.require_admin
def admintest(message):
    return "Admin only function executed"

if __name__ == "__main__":
    SYCSBot.run()
