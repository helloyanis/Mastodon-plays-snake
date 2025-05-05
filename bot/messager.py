from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv
import json, os
from snakeGame import SnakeGame
class Messager:
    def __init__(self):
        # Load environment variables from .env file and log in to Mastodon
        load_dotenv()
        self.initData = json.load(open('config.json'))
        print(os.environ.get("secret"))
        self.mastodon = Mastodon(
            access_token=os.getenv("secret"),
            api_base_url=self.initData["instance"]
        )
        print("Logged in as " + self.mastodon.me().username)
        self.statusId = None
        self.statusVisibility = self.initData["visibility"]
        self.delay = self.initData["delay"]

        #Start the game if it is not already started
        self.gameStatus = self.getGameStatus()
        if self.gameStatus is None:
            print("No game is happening, starting a new one...")
            self.statusId = self.sendNewGameStatus()
            # Write the status ID to the config file
            # self.initData["statusId"] = self.statusId
            # with open('config.json', 'w') as f:
            #     json.dump(self.initData, f, indent=4)
        else:
            print("A game is already happening!")
            self.statusId = self.gameStatus.id
        print ("Game status ID: " + str(self.statusId))
        print(self.waitAndGetPollResult())
    
    def getGameStatus(self):
        # Get the message the game is happening in. If it doesn't exist, return None
        statusId = self.initData["statusId"]
        status = None
        if statusId is None or statusId == "":
            # Nothing was passed during bot initialization but a game might still be happening, check that!
            if self.statusId is not None:
                statusId = self.statusId
                # Found a game, return the data by fetching the status
                status = self.mastodon.status(statusId)
                return status
        else:
            # A game is happening (from data passed at initialization), return the data by fetching the status
            status = self.mastodon.status(statusId)
            return status
        return None
    
    def sendNewGameStatus(self):
        # Send a new game status to the Mastodon instance
        poll = self.mastodon.make_poll(
            options=["⤴️ Turn Left", "➡️ Go Forward", "⤵️ Turn Right"],
            expires_in=self.delay
        )
        status = self.mastodon.status_post("A new game has started!", visibility=self.initData["visibility"], poll=poll) #TODO edit this
        self.statusId = status.id
        return status.id
    
    def waitAndGetPollResult(self):
        listener = PollListener(self.statusId)
        print("Listening for poll expiration...")
        self.mastodon.stream_user(listener)

class PollListener(StreamListener):
    def __init__(self, expected_status_id):
        self.expected_status_id = expected_status_id

    def on_notification(self, notification):
        if notification['type'] == 'poll':
            poll_status_id = notification['status']['id']
            if str(poll_status_id) == str(self.expected_status_id):
                print("Poll expired. Options:")
                for option in notification['status']['poll']['options']:
                    print(f"{option['title']}: {option['votes_count']} votes")
                # You could trigger further game logic here


messager = Messager()