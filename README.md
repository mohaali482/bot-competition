# ASTU Course Outline Bot.


This bot is a telegram bot used to give students course outlines. This bot has three type of users **superuser,** **admins,** and **normal users.**
It has been developed in **python3** using the module **python-telegram-bot.**


We/I chose this module because first it is free, second it has a large community and it doesn't have vulnerabilities atleast at the time of developing this project.


## Functionalities of the Bot.

For now this bot can do the following things.


## User functionalities are.


1. Search for course outlines
2. Get recent course outlines specific to the user.
3. Give reports on the courses.
4. Users can choose their own department to get updates.
5. Give feedback on the bot.


## Admins functionalities are.


1. Create update and delete course outlines
2. Read feedbacks
3. Read reports of the users.


## Superuser functionalites are.


1. Promote users to admins.
2. Demote admins.
3. Get list of users.
4. Get reports of course outline that are published.
5. Get Logs


## Installation Process
**First, run this command**

```pip install -r requirements.txt ```

This is used to install the requirements for the bot.

**Then, create a .env file**
Inside the .env file add this items.
```
ConnectionString = mongodb://**your database link**
API = **Your API Key**
SuperUser = '[**"superuser telegram usernames" **]'
```
**Lastly If your school system is different from the given change it in ```plugins/json files/``` and insert your school system using a json format**

After doing this steps you are now ready to run the bot.

To run the bot run the following command.
```python main.py```

After running this command the bot will start running.

