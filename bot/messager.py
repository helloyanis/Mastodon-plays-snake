from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv
import json, os, time, copy
from snakeGame import SnakeGame
class Messager:
    def __init__(self):
        # Load environment variables from .env file and log in to Mastodon
        load_dotenv()
        self.initData = json.load(open('config.json'))
        self.mastodon = Mastodon(
            access_token=os.getenv("secret"),
            api_base_url=self.initData["instance"]
        )
        print("Logged in as " + self.mastodon.me().username)
        if not self.mastodon.stream_healthy():
            print("Stream is not healthy! Try restarting in a few minutes (previous stream might still be connected?!).")
            return
        self.statusId = None
        self.statusVisibility = self.initData["visibility"]
        self.delay = self.initData["delay"]
        self.snakeGame = SnakeGame(width=10, height=10, initial_length=3, modifiers=None, save_file="snake_game.json")
        self.fruits_eaten = copy(SnakeGame.fruits_eaten)

        while True:
            #Start the game if it is not already started
            self.gameStatus = self.getGameStatus()
            if self.gameStatus is None:
                print("No game is happening, starting a new one...")
                self.statusId = self.sendNewGameStatus()
                # Write the status ID to the config file
                self.initData["statusId"] = self.statusId
                with open('config.json', 'w') as f:
                    json.dump(self.initData, f, indent=4)
                # Update profile fields with the amount of games started
                self.updateProfileFields(games_started_change=1, fruits_eaten_change=0)
            else:
                print("A game is already happening!")
                self.statusId = self.gameStatus.id
                self.updateGameStatus()
            print ("Game status ID: " + str(self.statusId))

            results = self.waitAndGetPollResult()
            # Update the game state based on the poll results
            self.updateProfileFields(games_started_change=1, fruits_eaten_change=0)
            if results is not None:
                self.moveSnake(results)
                

    
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
            options=["Turn left", "Go forward", "Turn right"],
            expires_in=self.delay
        )
        status = self.mastodon.status_post("Vote below to play Snake!\n"+self.snakeGame.display(), visibility=self.initData["visibility"], poll=poll) #TODO edit this
        self.statusId = status.id
        return status.id
    
    def updateGameStatus(self):
        # Check if the snake has eaten a fruit and update the profile fields accordingly
        if self.snakeGame.fruits_eaten > self.fruits_eaten:
            self.updateProfileFields(games_started_change=0, fruits_eaten_change=self.snakeGame.fruits_eaten - self.fruits_eaten)
            self.fruits_eaten = self.snakeGame.fruits_eaten
        # Update the game status with the current game state
        poll = self.mastodon.make_poll(
            options=["Turn left", "Go forward", "Turn right"],
            expires_in=self.delay
        )
        if not self.snakeGame.alive:
            # If the snake is dead, end the game and update the status
            self.mastodon.status_update(status="💥 Game over! The snake has died. I started a new game, check on my profile!\n"+self.snakeGame.display(), id=self.statusId, poll=poll)
            # Delete the snake_game.json file to reset the game
            os.remove("snake_game.json")
            self.snakeGame = SnakeGame(width=10, height=10, initial_length=3, modifiers=None, save_file="snake_game.json")
            return
        else:
            self.mastodon.status_update(status="Votes are closed, I have updated the game state and posted a new poll! Check on my profile.\n"+self.snakeGame.display(), id=self.statusId, poll=poll)
        newStatus = self.mastodon.status_post(status="📊 Vote below to play Snake! 🐍\n"+self.snakeGame.display(), poll=poll)
        # Update the status ID in the config file
        self.initData["statusId"] = newStatus.id
        with open('config.json', 'w') as f:
            json.dump(self.initData, f, indent=4)

    
    def waitAndGetPollResult(self):
        print("Waiting for poll to expire...")
        time.sleep(self.delay + 5)  # Wait for the poll to expire
        # Get the poll results
        poll = self.mastodon.status(id=self.statusId)["poll"]
        return poll

    def updateProfileFields(self, games_started_change=1, fruits_eaten_change=0):
        # Get the current fields
        oldFields = self.mastodon.me().fields
        if not oldFields or len(oldFields) < 2:
            # If there are no fields or too few, initialize them
            newFields = [
                ("Games started", str(games_started_change)),
                ("Total fruits eaten", str(fruits_eaten_change)),
                ("Source code", "https://github.com/helloyanis/Mastodon-plays-snake")
            ]
        else:
            # Parse existing values
            previousGamesStarted = int(oldFields[0]["value"])
            previousFruitsEaten = int(oldFields[1]["value"])
            newFields = [
                ("Games started", str(previousGamesStarted + games_started_change)),
                ("Total fruits eaten", str(previousFruitsEaten + fruits_eaten_change)),
                ("Source code", "https://github.com/helloyanis/Mastodon-plays-snake")
            ]

        self.mastodon.account_update_credentials(fields=newFields)

    def moveSnake(self, results):
        # Move the snake based on the poll results
        print("Poll results:")
        for option in results['options']:
            print(f"{option['title']}: {option['votes_count']} votes")
        # Get the direction with the most votes
        max_votes = max(option['votes_count'] for option in results['options'])
        winning_options = [option for option in results['options'] if option['votes_count'] == max_votes]
        if len(winning_options) > 1:
            print("Tie detected!")
            # Handle tie situation (e.g., choose randomly or keep the current direction)
            self.snakeGame.move()
        else:
            winning_option = winning_options[0]['title']
            if winning_option == "Turn left":
                self.snakeGame.turn("LEFT")
            elif winning_option == "Turn right":
                self.snakeGame.turn("RIGHT")
            else:
                self.snakeGame.move()
        # Check if the snake has died
        if not self.snakeGame.alive:
            print("Game over!")

messager = Messager()