import slack,time,io

from contextlib import redirect_stdout,redirect_stderr

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
    
    def command_args(self, parser):
        """
            Function decorator to more easily parse arguments.
        
            parser: Some argument parsing object (argparse.ArgumentParser)
                    which has child function parse_args, returning a dict
                    of named arguments.
        """
        def makeWrapper(func):
 
            def wrapper(message):
                args = message['text'].split(" ")[1:]
                with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
                    try:
                        args = vars(parser.parse_args(args))
                        output = buf.getvalue()
                        if len(output):
                            bot.say_in_channel(f"```{output}```", message['channel'])
                    except SystemExit:
                        output = buf.getvalue()
                        if len(output):
                            self.post_message(f"```{output}```", message['channel'])
                        return
                return func(message, args)

            return wrapper
                
        return makeWrapper 

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
        else:
            response = '<@' + user + '> ' + default_response
    
        if response == None: return
        
        self.post_message(response, channel)

    def setup_bot_events(self):
        self.slack_rtm.on(event='message', callback=self.handle_message)

    def run(self):
        print("SYCS Bot Running")
        self.slack_rtm.start()
