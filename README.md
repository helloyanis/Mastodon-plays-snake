# Mastodon plays snake
Source code for a bot that lets you play snake on Mastodon!

Requirements
----------------
- Python
- Mastodon.py, install it with :

```ps1
py -m pip install Mastodon.py
```

Create an account on a Mastodon instance (Careful, `mastodon.social` has lots of rate limits! I recommend `mstdn.social` as this is what I used when testing)

In your user settings, check `This is a bot account`, then go to `applications` and create a new application, and give it a name.

Below, there are some boxes you'll need to check to give the bot permissions. You'll need :

- `read:notifications` to get notified when a poll ends
- `read:statuses` to read the poll's votes
- `profile` to read the account's fields (for the amount of games started and fruits eaten)
- `write:accounts` to update the account's fields (for the amount of games started and fruits eaten)
- `write:statuses` to post and edit the messages when the game ends

Then save your changes, open your created app and note the `access token`. DON'T SHARE IT WITH ANYONE! This is the key to your account.

Then, create a file called `.env` in the `/bot` folder and add the following lines to it:

```env
secret="YOUR_ACCESS_TOKEN"
```

You'll also need to edit the `config.json` file at the root of this repository.
- `instance` is the URL of your Mastodon instance (e.g. `https://mstdn.social`)
- `statusID` is the ID of the message that will be used to start the game. You can get it by clicking on the message and copying the URL. The ID is the last part of the URL. If you leave it empty, the bot will create a new message. This will automatically update this field in the config file, so you can leave it empty.
- `visibility` is the visibility of the message. You can set it to `public`, `unlisted`, `private` or `direct`. For testing, use `direct` so only you can see the message. Otherwise, use `public`, [more info here](https://mastodonpy.readthedocs.io/en/stable/05_statuses.html#mastodon.Mastodon.status_post).
- `delay` is the amount of time in seconds that each poll lasts.

Finally run the `messager.py` file inside the `/bot` folder. This will start the bot and you'll be able to play snake on Mastodon!

## Troubleshooting
 - `mastodon.errors.MastodonNotFoundError` : This means that the bot is trying to access a message that doesn't exist. This can happen if you delete the message or if the bot is trying to access a message that was never created. To fix this, delete the `statusID` field's value (usually a number) in the `config.json` file, leave only empty quotes.

 <a rel="me" href="https://mstdn.social/@snakebot"></a><a rel="me" href="https://furries.club/@helloyanis"></a>