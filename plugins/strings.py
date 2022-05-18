# Start message
start_message = '''
Welcome {first_name}, How are you? Hope you are doing well, \n I'm <b>{bot_name}</b>
To get the list of commands send /help.
'''

# Help message displayed for normal users.
normal_message = '''
Hello, Welcome to <b>{first_name}.</b>
I'm a bot to help you get any course outline if you are in <b>Astu.</b>😊

⚫ Search for course outline
⚫ Recent course outlines related to your department
⚫ Report missing course outline.
⚫ Tell me your department inorder to get the most recent course outlines to your department.

'''

# Help message displayed for admin users.
admin_message = '''<b>Admin Privileges</b>

You are my master or an admin as you humans say it. You can do the following things.

🟣 Post course outlines.
🟣 Delete course outlines.
🟣 Update course outlines.
🟣 Read reports.

<b>You are made my master for a reason by my creator, so don't mess up anything.I'll be reporting everything to my creator ok 😊. Have a nice time.</b>


'''

# Help message displayed for superadmin users.
super_message = '''<b>Welcome back creator.</b>

How can I serve you today. Let me remind you the things you can order me.


🟢 Promote users to admin.
🟢 Demote admins back to users.
🟢 Post course outlines.
🟢 Delete the course outlines.
🟢 Update the course outlines.
🟢 See full information about the users of the bot.
🟢 Get the report on the new updates made by the admins.
🟢 Read comments on the course outlines.
🟢 Read comments on the bot.

'''

# Help message displayed for superadmin user, including the normal message that is seen by the normal users.
main_message = super_message + '''
<b>Here is the message that the normal users see </b> 

{help}

 You can also use this properties too.'''

# Message that tells the format of the course insertion.
course_insertion_message = '''Enter the course name and course code in the following format.
 
 <b><i>coursecode - course name</i></b>
 '''

# The cancel message.
cancel_message = '''
The command has been cancelled. Anything else I can do for you?

Send /help for a list of commands.
'''

cancel_message_2 = '''
\n\n If you don't want to edit anything just send /cancel .\n\n
'''

canceled = '''
Ok then cancelled. 👍
'''


# The report message that is used to help to report missing course outlines.
report_message = '''
Tell me the missing course outline.
'''


# The report success message that is sent to tell the user that the report is reported successfully.
report_success = '''
Ok, the report will be delivered to authorities.
'''


# A message that helps the user to choose his/her department.
department_text = '''
Please choose your department.
'''

# A message that is displayed when the user access the recent and hasn't registered the department
error_department = '''
You have to register your department in order to proceed.
'''

# A message that is displayed when a user wants to give feedback about the bot.
feedback_message = '''
Your feedback means a lot tell me something that my father should improve.
'''

# A message that is displayed when the user has finished giving the feedback.
gratitude_message = '''
Thank you for your feedback. I'll tell my father and my masters.
'''

# Messages displayed to the superuser
manage_message = '''
Here father this are the things you can do.
'''

who_message = '''
Who do you want to make my master. Tell me thier username.
'''

who_demote_message = '''
From my masters tell my who do you want me to forget. Tell me thier username.
'''

already_admin = '''
User is already an admin or aka my master.
'''

not_admin = '''
User is not admin.
'''

made_admin = '''
Made the user my master.
'''

made_not_admin = '''
Demoted the user.
'''

not_found = '''
Sorry, I don't know that user, father.
'''

# Messages displayed to the admins
congratulation_message = '''
Congragulations you are an admin. Send /start to see the new updates on your authority. Send /help to get help.
'''

sorry_message = '''
Sorry, my father dumped you. You're not my master anymore. Nice working with you.
'''

course_not = '''
Course not found. Try again.
'''

no_course_outlines = '''
No course outlines found. 🚫
'''

no_new_things = '''
Sorry there are no new things. 🚫
'''

no_data = '''
There is no data about that yet. 🚫
'''

here = '''
Here you go. 😊
'''

tell_me_code = '''
'Tell me the course code.'
'''

enter_code = '''
Please Enter the correct course code and name. In the correct format.
'''

code_exists = '''
Course code exists. Try again.
'''

insert_file = '''
 Insert the file. I will accept Image and PDF files. If you don\'t want just send /skip
 '''

done = '''
 Done.
 '''

choose_division = '''
Choose the Division
'''

choose_department = '''
Choose the Department
'''

no_logs = '''
There is no logs.
'''

deleted = '''
Deleted.
'''