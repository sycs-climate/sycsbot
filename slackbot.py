import slack,time

class SlackBot:

    starterbot_id = None
    RTM_READ_DELAY = 0.5

    def __init__(self, oauthtoken):
        self.token = oauthtoken
        self.slack_rtm = slack.RTMClient(token=self.token)
        self.slack_cli = slack.WebClient(token=self.token)
        self.setup_bot_events()

    def post_message(self, message, channel):
        return self.slack_cli.chat_postMessage(
            channel=channel,
            text=message
        )

    def get_user_info(self, user): # Probably pointless having this func
        return self.slack_cli.users_info(
            user=user
        )['user']

    commands = {}

    def register_command(self, keyword, callback):
        if keyword in self.commands:
            print(f"WARNING: Chat expression {keyword} already registered to callback {commands[keyword].__name__}. Re-registering to {callback.__name__}")

        self.commands[keyword] = callback
        print(f"Command {keyword} registered to callback {callback.__name__}")

    def command(self, keyword, **kwargs):
        def decorator(callback):
            self.register_command(keyword, callback)
            return callback
        return decorator

    def require_admin(self, func):
        def wrap(message):
            if not self.get_user_info(message['user'])['is_admin']:
                return f"<@{message['user']}> Sorry, only workspace administrators can use this command.."
            else:
                return func(message)
        return wrap
    
    def handle_message(self, **payload):
        """
            Executes bot command if the command is known
        """
        if 'subtype' in payload['data']: return

        channel = payload['data']['channel']
        user = payload['data']['user']
        text = payload['data']['text']
        
        if text[0] != '!': return # Only respond to cmds prefaced with !

        default_response = "I'm not sure what you mean. Use !help for help."
        response = None
        command = text.split()
        command[0] = command[0].lower()[1:]

        if(command[0] in self.commands):
            response = self.commands[command[0]](payload['data'])
            
        if response == None:
            response = '<@' + user + '> ' + default_response

        self.post_message(response, channel)

    def setup_bot_events(self):
        self.slack_rtm.on(event='message', callback=self.handle_message)

    def run(self):
        print("SYCS Bot Running")
        self.slack_rtm.start()
