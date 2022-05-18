import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.common import clean_node

load_dotenv()



ConnectionString = os.getenv('ConnectionString')

client = MongoClient(ConnectionString)



# Database of the bot.
db = client['bot']

# Collection of the users.
users = db['users']

# Collection of the course outlines.
course_outlines = db['course_outlines']

# Collection of the comments.
comments = db['comments']

# Collection of the reports.
reports = db['reports']

# Collection of the feedbacks.
feedbacks = db['feedback']