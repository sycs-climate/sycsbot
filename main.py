import os
import time
import re
import json
from slackclient import SlackClient

with open('oauthtoken.txt', 'r') as f:
    token = f.read().strip()
    f.close()

slack_client = SlackClient(token)
starterbot_id = None

RTM_READ_DELAY = 0.5

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            if event['text'].strip().startswith('!'):
                handle_command(event['text'].strip()[1:], event["channel"], event['user'])


def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    default_response = "I'm not sure what you mean. Use !help for help."
    response = None
    command = command.split()
    command[0] = command[0].lower()

    if command[0] == 'setup':
        if not get_user_info(user)['is_admin']:
            response = 'Sorry, only workspace administrators can use !setup commands.'
        else:
            if command[1].lower() == 'channel':
                with open('channels.json', 'r') as f:
                    fc = json.loads(f.read())
                    f.close()
                fc[command[2].lower()] = channel.lower()
                with open('channels.json', 'w') as f:
                    f.write(json.dumps(fc))
                    f.close()
                response = 'Successfully set #' + command[2].lower() + ' to channel ' + channel.lower() + '.'

    elif command[0] == 'getchannel':
        response = get_channel(command[1]) or 'Channel not set up yet. Use !setup channel <channel name> in the channel to set it up.'

    else:
        response = default_response

    post_message(response, channel)

def post_message(message, channel):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

def get_user_info(user):
    return slack_client.api_call(
        "users.info",
        user=user
    )['user']

def get_channel(channel_name):
    with open('channels.json', 'r') as f:
        fc = json.loads(f.read())
        f.close()
    if channel_name in fc:
        return fc[channel_name]
    return None

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("SYCS Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            parse_bot_commands(slack_client.rtm_read())
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
