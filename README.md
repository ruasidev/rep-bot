# rep-bot
Project for CS 321

## Description
Discord bot that does sentiment analysis on chats over time and builds a reputation for each user. 
### Problem:
- Users in Discord servers and in online chats in general are not able to see how toxic / nice someone is before interacting with them. 
- Banning toxic users is also difficult since it's common to ban someone who is rarely toxic when they say something mean once. 
### Approach:
Banning a user for being toxic one time isn't really fair. Enforcement should happen differently for known-toxic users than for normal / nice users. 
A good idea would be to take a similar approach to how laws are enforced in the US: **people without a criminal record aren't punished as harshly when they break the law as those with a criminal record**. 
If someone who is usually nice is toxic to someone one time, they shouldn't be punished as hard as someone who's always toxic and continues to be. 
### Solution:
We can build public profiles of users that show their reputation by analyzing chats with context-aware sentiment analysis. We can add a leaderboard to make it more incentivizing to be nice; would make people literally compete to see who can be nicer
- makes it easy for users to tell who to avoid
- makes it easy for moderators and admins to adjust how they react to toxic behavior from users
- gives users an incentive to uphold their reputation and maintain a positive chat history

(this entire idea is really just the social credit system im crying)
### Incorporating a database
The solution calls for one naturally which is nice
- SQLite database that runs in the system the bot is hosted on
- One row per user with a reputation score 1-5 (stars)
- Keep records of chats that have poor sentiment and a FK to the user who sent it (+ when it was sent)
### Incorporating UI
- Dashboard for admins that shows stuff that not everyone else can see, like chats we recorded that lowered their reputation
- Admins could also delete chats from someones history if we find that it's an unfair assessment given the context they sent the chat in (e.g. quoting someone else, inaccurate sentiment score, etc)
- A few settings that admins can tweak (e.g. weights)
- Suggestions to ban users with low reputation + reason
### Incorporating AI chatbot API
Last `n` messages can be given to the chatbot to assess the sentiment of each message *contextually*, since sentiment analysis word-for-word tends to be inaccurate/harsh. 
After researching, good news is that an LLM is literally the best tool for exactly this, so it's a perfect fit

The bot can react to messages that are poor sentiment and give verbal warnings to people.
