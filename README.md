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

# Requirements Elicitation

Notes, recordings, and images we collected while figuring out what rep-bot should do. Most of what we found falls into three groups: people getting punished over one message with no context, automated filters that only match words, and moderators wanting punishments to depend on someone's history.

## Notes (comments and articles from online)

### People punished over a single message, without context

1. **Steam forums, "can you maybe tweak the automod filters" (Apr 2025)**
   https://steamcommunity.com/discussions/forum/0/530969757695920324
   - episoder, after getting banned for breaking up an argument: "i seriously question the human there, that failed to see the logic and intend of the post."
   - Tito Shivan: "You have a bunch of people being paid to deal with reports in bulk, more than often context isn't even considered."
   - **Takeaway:** reports get handled one post at a time, and the context around the post gets lost.

2. **Helldivers 2 Discord bans (Feb 2024)**
   https://steamcommunity.com/app/553850/discussions/0/7599331177362361063
   - Quagimus: "I've met a few others who also got banned like I did. No warning, No timeout, just deletus"
   - **Takeaway:** users went straight to a ban with no warning step in between.

3. **Helldivers 2 Discord, mass bans over emoji reactions (Jun 2024)**
   https://steamcommunity.com/app/553850/discussions/0/6171700864785697842
   - Onnajy: "30 people got banned for reacting negatively within a 1-minute time frame" and "The actual implication is worrying still though if they're banning people without warning."
   - (Other people in the thread dispute the details, but the complaint about no warnings is common.)
   - **Takeaway:** one reaction got treated the same for everyone, no matter their history.

4. **r/Unity3D, "Discord containment thread" (Dec 2024)**
   https://redlib.hackliberty.org/r/Unity3D/comments/1hhm87e/discord_containment_thread/m2sbn77/?context=3
   - u/bendgk: "I'm the guy who got banned by Fogsight for reacting with "F" "O" "G"."
   - **Takeaway:** a ban over a single reaction.

5. **Phasmophobia Discord ban (Oct 2023)**
   https://steamcommunity.com/app/739630/discussions/0/6770657890633484320
   - Axezebra: "i sent a gif that wasn't even anything bad and i got banned"
   - (A moderator in the thread says there was a reason, but the user never saw it.)
   - **Takeaway:** users often don't know why they were punished. Showing people their rating, and letting mods see the flagged messages, makes this more transparent.

### Automated filters only match words

6. **Discord Moderator Academy, "Auto Moderation in Discord"**
   https://discord.com/moderation/1500000178701-321-auto-moderation-in-discord
   - Discord's own guide says keyword filters don't account for context, and recommends sending alerts instead of blocking for words that are often used innocently.
   - **Takeaway:** even Discord admits AutoMod can't read context.

7. **PeakBot, "How to fix Discord AutoMod false positives"**
   https://peakbot.pro/blog/how-to-fix-discord-automod-false-positives
   - "It does not understand meaning."
   - A filter for "ass" also triggers on "class" and "assist."

8. **Wikipedia, "Scunthorpe problem"**
   https://en.wikipedia.org/wiki/Scunthorpe_problem
   - The well-known name for filters blocking innocent text because it contains a "bad" string. In 1996, AOL's filter stopped people from Scunthorpe, England from making accounts.

9. **Techdirt, "Content Moderation Case Study: Detecting Sarcasm Is Not Easy (2018)"**
   https://www.techdirt.com/tag/sarcasm/
   - Twitter suspended accounts for sarcastic tweets like "kill me" because enforcement relied on keywords.
   - **Takeaway:** sarcasm and jokes need context, which is the main reason we're using an LLM that reads the last n messages.

10. **Gizmodo, "Discord goes ban happy, suspends people for benign images" (Jul 2026)**
    https://gizmodo.com/discord-goes-ban-happy-suspends-people-for-benign-images-2000782587
    - Discord's automated system wrongly banned more than 8,000 users for harmless images like chessboards and Minecraft inventories. The article's subtitle: "The auto-mod is out of control."
    - **Takeaway:** automated punishment with no human review goes wrong fast. Rep-bot only suggests bans; a moderator always makes the call.

11. **Bodyguard, "Keyword-based moderation: why it no longer works"**
    https://www.bodyguard.ai/en/blog/keyword-based-moderation-why-it-no-longer-works-2026
    - "A keyword-based moderation system blindly blocks any content containing a banned term, with zero understanding of context."

### Support for our approach

12. **Pavlopoulos et al., "Toxicity Detection: Does Context Really Matter?" (ACL 2020)**
    https://arxiv.org/abs/2006.00998
    - "We find that context can both amplify or mitigate the perceived toxicity of posts."
    - Some posts got the *opposite* toxicity label when annotators couldn't see the conversation around them.
    - **Takeaway:** research backs up judging each message together with the messages around it.

13. **PeakBot, "Timeout vs. kick vs. ban: the escalation ladder"**
    https://peakbot.pro/blog/discord-timeout-vs-kick-vs-ban-escalation-ladder
    - "a clean record gets a warning, a member with three prior timeouts this month gets a temp ban."
    - "A ladder only works if you can see where someone already stands on it."
    - **Takeaway:** moderators already want punishments based on history. Right now they have to track that history by hand.

14. **MEE6 Moderator plugin docs**
    https://wiki.mee6.xyz/plugins/moderator
    - MEE6 can escalate automatically once someone hits a number of warnings in a time window (for example, a ban after 10 warnings in 14 days).
    - **Takeaway:** the closest thing that exists today, but it only counts warnings. It doesn't look at how someone usually behaves, and the warnings themselves still come from word filters.

## Recordings (people using similar tools)

Setup tutorials for the tools we compared against: keyword lists, spam filters, and punishments based on warning counts. None of these tools look at the conversation around a message or at the person's overall history.

- How to Set Up Discord AutoMod (Full Guide): https://www.youtube.com/watch?v=13Xe-KKU6V4
- Advanced Discord AutoMod Setup: https://www.youtube.com/watch?v=6-DL1NFwE6w
- Managing MEE6 - Automod Automated Actions: https://www.youtube.com/watch?v=CGSrYz_reKQ
- Set Up Auto Moderation with Carl-bot (2025): https://www.youtube.com/watch?v=rayK8jVRuoY

## Images

- `rep-command-mockup.png`: a mockup of what the `/rep` reply could look like.
- System model diagram (in our deliverable document).
- TODO: screenshots of Discord's AutoMod settings page and MEE6's automod dashboard.

