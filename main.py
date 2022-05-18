import json
import logging

import requests
from telegram.ext import *

from plugins.excel import *
from plugins.connection import *
from plugins.documents import *
from plugins.keyboards import *
from plugins.Settings import *
from plugins.strings import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO,filename=LOGS_DIR)
logger = logging.getLogger(__name__)



with open('plugins/json files/school_system.json') as f:
    SCHOOL_SYSTEM = json.load(f)

'''Needed for the post conversation handler'''
COURSE_NAME, COURSE_DATA, REST=range(3)

'''Needed for the search conversation handler'''
FIRST = 5

UPDATE, UPDATE_COURSE_NAME, UPDATE_COURSE_DATA, DELETE = range(6,10) 
PROMOTE, DEMOTE =range(1,3)

def help(update: Update, context: CallbackContext):

    help_message = normal_message.format(first_name = context.bot.first_name)

    user = update.message.from_user
    
    if is_superuser(user):
        message = main_message.format(help = help_message)
    
    elif is_admin(user):
        message= help_message + admin_message
    
    else:
        message = help_message

    logger.info(f'User : @{user.username} asked for help')

    update.message.reply_text(
        text = message,
        parse_mode = ParseMode.HTML
    )


# Used to start the bot
def start(update: Update, context: CallbackContext):
    user = update.message.from_user

    if check_user(user.id):
        pass
    else:
        save_user(user)


    reply_markup = ReplyKeyboardMarkup(normal_buttons,resize_keyboard=True)
    
    if is_admin(user):
        reply_markup = ReplyKeyboardMarkup(normal_buttons + admin_buttons,resize_keyboard=True)
    
    if is_superuser(user):
        reply_markup = ReplyKeyboardMarkup(normal_buttons + admin_buttons + superadmin_buttons , resize_keyboard=True)

    logger.info(f'User : @{user.username} started the bot')
    
    update.message.reply_text(
        text=start_message.format(first_name = user.first_name, bot_name = context.bot.first_name),
      parse_mode=ParseMode.HTML,reply_markup= reply_markup
    )



# Used to get the course name while uploading a new course outline
def course_name(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text
    try:
        course_code, course_description = text.split('-')
        
        course_code.replace(' ','')
        course_description.replace(' ','')
        if len(course_description)<3 or len(course_code)<3:
            update.message.reply_text(
                enter_code
            )
            return COURSE_NAME
        if check_course(course_code):
            update.message.reply_text(
                'Course already exists try again.'
            )

            return COURSE_NAME
        
        user_data['course_name'] = course_description
        user_data['course_code'] = course_code
    except:
        update.message.reply_text(
                enter_code
        )
        return COURSE_NAME

    update.message.reply_text(
        f'Insert the file of {course_description}. I will accept Image and PDF files.'
    )

    return COURSE_DATA


# Used to get the course data image only while uploading a new course outline
def course_data_image(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_data = context.user_data
    text = update.message
    try:
        file_id = text['photo'][-1]['file_id']
        file = context.bot.getFile(file_id)
        file.download(f'{FILE_DIR}images/{file_id}.jpg')
        context.user_data['course_data'] = file_id
        user_data['photo'] = True
    except:

        pass
    
    logger.info(f'User : @{user.username} saved a new course outline by the code of {user_data["course_code"]} and name of {user_data["course_name"]}')

    user_data['username'] = user.username
    save_course(user_data, user, logger)

    update.message.reply_text(
        done
    )

    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END


# Used to get the course data document only while uploading a new course outline
def course_data_document(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    text = update.message

    try:
        file_ext = text['document']['file_name'].split('.')[-1]
        if file_ext != 'pdf' and file_ext !='jpg' and file_ext != 'png':
            update.message.reply_text(
                'The document file must be pdf or image.'
            )
            return COURSE_DATA

        file_id = text['document']['file_id']
        file = context.bot.getFile(file_id)
        file.download(f'{FILE_DIR}documents/{file_id}.pdf')
        user_data['course_data'] = file_id
        user_data['photo'] = False

    except:
        pass


    user_data['username'] = user.username
    save_course(user_data,user,logger)

    update.message.reply_text(
        done
    )
    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END



# Used to get the rest of information of the course outline.
def rest_info(update: Update, context: CallbackContext):
    user_data = context.user_data
    query = update.callback_query

    clicked = user_data['clicked']
    data = query.data

    if data == 'back':
        clicked.pop()
    else:
        clicked.append(data)

    user_data['clicked'] = clicked


    if data == 'sem 1' or data == 'sem 2':
        message = course_insertion_message
        query.edit_message_text(message, parse_mode = ParseMode.HTML)

        return COURSE_NAME

    copy_of_courses = SCHOOL_SYSTEM
    for click in clicked:
        copy_of_courses = copy_of_courses[click]

    if type(copy_of_courses)==dict:
        keys = copy_of_courses.keys()
    else:
        keys = [i[0] for i in copy_of_courses]

    keyboard = []
    for key in keys:
        keyboard.append([InlineKeyboardButton(text=key, callback_data=key)])

    if clicked:
        keyboard.append([InlineKeyboardButton(text='🔙', callback_data='back')])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    messages = ['Division', 'School', 'Department', 'Year', "Semester"]

    if len(clicked):
        if '2nd_1st' in clicked:
            user_data['clicked'].append('2nd Year')
            user_data['clicked'].append('sem 1')
            user_data['clicked'].remove('2nd_1st')
            message = course_insertion_message
            query.edit_message_text(message, parse_mode = ParseMode.HTML)

            return COURSE_NAME

        elif clicked[0]=='Fresh':
            query.edit_message_text(f'Choose the {messages[-1]}', reply_markup = reply_markup)
        elif clicked[0]=='Applied':
            query.edit_message_text(f'Choose the {messages[len(clicked)+1]}', reply_markup = reply_markup)
        else:
            query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)
    else:
        query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)



# Used to end any conversation.
def end(update: Update, context: CallbackContext):
    user_data = context.user_data
    update.message.reply_text(cancel_message)

    user_data = clean_user_data(user_data)
    return ConversationHandler.END


# Used to start a convesation to search courseoutlines.
def search(update: Update, context: CallbackContext):
    user_data = context.user_data
    reply_message = choose_division

    user_data['clicked'] = []

    keyboard = []
    
    for key in SCHOOL_SYSTEM:
        keyboard.append([InlineKeyboardButton(key,callback_data=key)])

    reply_markup = InlineKeyboardMarkup(keyboard)
        
    update.message.reply_text(reply_message,reply_markup = reply_markup)

    return FIRST


# Used to enter the data needed to search courseoutlines.
def rest_info_search(update: Update, context: CallbackContext):
    user_data = context.user_data
    query = update.callback_query
    user = query.from_user

    clicked = user_data['clicked']
    data = query.data
    query.answer()


    if data == 'back':
        if 'courses' in user_data:
            del(user_data['courses'])
        clicked.pop()
    else:
        clicked.append(data)
    
    if data != 'back' and 'courses' in user_data :
        user_data.clear()
            
        document = check_course(data)
        increment = {"$inc":{'downloads':1}}
        course_outlines.update_one(document,increment)

        logger.info(f'User : @{user.username} requested a course outline by the code of {document["code"]} and name of {document["name"]}')


        query.edit_message_text(text=f'{document["name"]}')
        if document['photo']:
            context.bot.send_photo(update.effective_chat.id, photo = document['file'])
        else:
            context.bot.send_document(update.effective_chat.id, document['file'])

        user_data = clean_user_data(user_data)

        return ConversationHandler.END
        

    user_data['clicked'] = clicked


    if data == 'sem 1' or data == 'sem 2' or data == '2nd_1st':
        if '2nd_1st' in user_data['clicked']:
            user_data['clicked'].append('2nd Year')
            user_data['clicked'].append('sem 1')
            user_data['clicked'].remove('2nd_1st')

        document = document_creator(user_data)
        course_list = list(course_outlines.find(document))
        
        keyboard = []
        for element in course_list:
            keyboard.append([InlineKeyboardButton(f'{element["name"]} - {element["code"]}', callback_data=f'{element["code"]}')])

        keyboard.append([InlineKeyboardButton(text='🔙', callback_data='back')])
        user_data['courses']=True
        reply_markup = InlineKeyboardMarkup(keyboard)

        if len(keyboard) == 1:
            query.edit_message_text(
                no_course_outlines,
                reply_markup=reply_markup
            )
        else:
            query.edit_message_text('Select one', reply_markup=reply_markup)

    else:
        copy_of_courses = SCHOOL_SYSTEM
        for click in clicked:
            copy_of_courses = copy_of_courses[click]

        if type(copy_of_courses)==dict:
            keys = copy_of_courses.keys()
        else:
            keys = [i[0] for i in copy_of_courses]

        keyboard = []
        for key in keys:
            keyboard.append([InlineKeyboardButton(text=key, callback_data=key)])

        if clicked:
            keyboard.append([InlineKeyboardButton(text='🔙', callback_data='back')])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        messages = ['Division', 'School', 'Department', 'Year', "Semester"]

        if len(clicked):
            if clicked[0]=='Fresh':
                query.edit_message_text(f'Choose the {messages[-1]}', reply_markup = reply_markup)
            elif clicked[0]=='Applied':
                query.edit_message_text(f'Choose the {messages[len(clicked)+1]}', reply_markup = reply_markup)
            else:
                query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)
        else:
            query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)



# Used to start a conversation to enable users to report missing courseoutline.
def report(update: Update, context: CallbackContext):
    update.message.reply_text(
        report_message
    )

    return FIRST


# Used to store all the data of the report to be submitted.
def report_data(update: Update, context: CallbackContext):
    message = update.message.text
    user_data = context.user_data
    user = update.message.from_user

    user_data['username'] = update.message.from_user.username
    user_data['report'] = message

    save_report(user_data)
    
    logger.info(f'User : @{user.username} reported a missing course outline')

    update.message.reply_text(
        report_success
    )

    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END


# Used to get recent course outlines related to the department.
def recent(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    recent_courses = get_recent(user)
    if recent_courses:
        replymarkup = InlineKeyboardMarkup(recent_courses)
        if len(recent_courses) == 1:
            update.message.reply_text(
                no_new_things
            )
        
            user_data = clean_user_data(user_data)
            return ConversationHandler.END

        logger.info(f'User : @{user.username} requested for recent adds.')
        update.message.reply_text(
            here,
            reply_markup=replymarkup
        )

        return FIRST

    else:
        update.message.reply_text(
            error_department
        )

        user_data = clean_user_data(user_data)
        return ConversationHandler.END


# Used to search courseoutlines using inline method
def inlinequery(update: Update, context: CallbackContext):
    query = update.inline_query.query

    if query == "":
        return
    
    courses = list_all_courses()
    results = []
    for course in courses:
        if query.lower() in course.lower():
            if courses[course][1]:
                results.append(InlineQueryResultCachedPhoto(course, courses[course][0], title=course.split('-')[0], description = course.split('-')[0]))
            else:
                results.append(InlineQueryResultCachedDocument(course, course.split('-')[1], courses[course][0],description = course.split('-')[0]))



    update.inline_query.answer(results)


# A function used to ask the department
def my_dept(update: Update, context: CallbackContext):
    keyboard = []
    user_data = context.user_data
    user = update.message.from_user

    dept = check_dept(user.id)
    message = ''
    for key in dept:
        if dept[key]:
            message += f"Your current {key} is {dept[key]}.\n"

    if message:
        message += cancel_message_2
    
    for i in SCHOOL_SYSTEM:
        keyboard.append([InlineKeyboardButton(i,callback_data=i)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    user_data['clicked'] = []
        
    update.message.reply_text(
        message + department_text,
        reply_markup = reply_markup
    )

    return FIRST


# A function used to store the department.
def rest_dept(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    
    clicked = user_data['clicked']
    data = query.data

    if data == 'back':
        clicked.pop()
    else:
        clicked.append(data)

    user_data['clicked'] = clicked

    copy_of_courses = SCHOOL_SYSTEM
    for click in clicked:
        copy_of_courses = copy_of_courses[click]

    if type(copy_of_courses)==dict:
        keys = copy_of_courses.keys()
    else:
        keys = [i[0] for i in copy_of_courses]

    if 'sem 1' in keys or 'sem 2' in keys or len(keys) == 0:

        logger.info(f'User : @{user.username} saved his/her department')
        
        save_dept(clicked, user)
        user_data.clear()
        query.edit_message_text(done)

        user_data = clean_user_data(user_data)
        return ConversationHandler.END

    keyboard = []
    for key in keys:
        keyboard.append([InlineKeyboardButton(text=key, callback_data=key)])

    if clicked:
        keyboard.append([InlineKeyboardButton(text='🔙', callback_data='back')])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    messages = ['Division', 'School', 'Department', 'Year',]

    if len(clicked):
        if clicked[0]=='Applied':
            query.edit_message_text(f'Choose the {messages[len(clicked)+1]}', reply_markup = reply_markup)
        else:
            query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)
    else:
        query.edit_message_text(f'Choose the {messages[len(clicked)]}', reply_markup = reply_markup)


# Used to fetch the course outline
def get_course(update : Update, context : CallbackContext):
    user_data = context.user_data
    query = update.callback_query
    user = query.from_user

    data = query.data

    if (data != 'cancel'):
        course = fetch_course(data)
        increment = {"$inc":{'downloads':1}}
        course_outlines.update_one(course,increment)

        query.edit_message_text(text=f'{course["name"]}')

        logger.info(f'User : @{user.username} recieved a course outline by the code of {course["code"]} and the name of {course["name"]}')
        
        if course['photo']:
            context.bot.send_photo(update.effective_chat.id, photo = course['file'])
        else:
            context.bot.send_document(update.effective_chat.id, course['file'])

    else:
        query.edit_message_text(
            canceled
        )

    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END

# Used to get the feedback of the user
def feedback(update: Update, context: CallbackContext):
    update.message.reply_text(
        feedback_message
    )

    return FIRST


# Get the feedback
def get_feedback(update: Update, context: CallbackContext):
    user_data = context.user_data
    feedback = update.message.text
    user = update.message.from_user
    save_feedback(user, feedback)

    logger.info(f'User : @{user.username} gave a feedback on the bot')

    update.message.reply_text(
        gratitude_message
    )

    user_data = clean_user_data(user_data)
        
    return ConversationHandler.END


def manage_admins(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_data = context.user_data

    if not is_superuser(user):
        user_data = clean_user_data(user_data)

        return ConversationHandler.END
    
    reply_markup = InlineKeyboardMarkup(manage_admins_buttons)

    update.message.reply_text(
        manage_message, 
        reply_markup=reply_markup
    )

    return FIRST


def manage_admin_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == 'promote':
        query.edit_message_text(
            who_message
        )
        return PROMOTE

    else:
        query.edit_message_text(
            who_demote_message
        )
        return DEMOTE


# A function to promote users
def promote(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    username = update.message.text
    username = username.replace('@','')
    username = username.replace(' ','')
    if find_user(username=username):
        if is_admin(username=username):
            update.message.reply_text(
                already_admin + " Try again"
            )

            return PROMOTE
        else:
            user_id = make_admin(username)
            update.message.reply_text(
                made_admin
            )

            context.bot.send_message(
                chat_id = user_id,
                text = congratulation_message
            )

            logger.info(f'User : @{user.username} made user @{username} admin.')

            user_data = clean_user_data(user_data)

            return ConversationHandler.END
    else:
        update.message.reply_text(
            not_found + " Try again"
        )

        return PROMOTE
    

# A function to demote users
def demote(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    username = update.message.text
    username.replace('@','')
    username.replace(' ','')
    if find_user(username= username):
        if not is_admin(username=username):
            update.message.reply_text(
                not_admin + " Try again"
            )

            return DEMOTE
        else:
            user_id = make_not_admin(username)
            update.message.reply_text(
                made_not_admin
            )

            context.bot.send_message(
                chat_id = user_id,
                text = sorry_message
            )

            logger.info(f'User : @{user.username} demoted user @{username}')

            user_data = clean_user_data(user_data)

            return ConversationHandler.END
    else:
        update.message.reply_text(
            not_found + " Try again"
        )

        return DEMOTE


# A function that gives the list of users
def list_of_users(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_superuser(user):
        return

    keyboard = [
        [InlineKeyboardButton('List of Admins', callback_data="admins")],
        [InlineKeyboardButton('Lisf of All Users', callback_data="users")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Please choose father",
        reply_markup=reply_markup
    )

    return FIRST


# A function that handles query that is queried by the superuser
def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data
    user = query.from_user
    data = query.data

    if data == 'admins':
        DIR = generate_file_admins()
    elif data == 'users':
        DIR = generate_file()

    document = open(DIR, "rb")
    if os.stat(DIR).st_size == 0:
        query.edit_message_text(
            no_data
        )
    else:
        query.edit_message_text(
            here
        )

        logger.info(f'User : @{user.username} requested the list of admins')

        context.bot.send_document(
            query.message.chat_id,
            document
        )

    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END


# A function to generate feedbacks
def feedbacks_list (update: Update, context : CallbackContext):
    user = update.message.from_user

    if not is_admin(user) and not is_superuser(user):
        return
    
    DIR = generate_feedbacks()

    document = open(DIR, "rb")
    if os.stat(DIR).st_size == 0:
        update.message.reply_text(
            no_data
        )
    else:
        update.message.reply_text(
            here
        )
        logger.info(f'User : @{user.username} requested the list of feedbacks')
        context.bot.send_document(
            update.message.chat_id,
            document
        )
    

# A function to give reports on the course to the superuser
def report_course(update: Update, context: CallbackContext):
    user = update.message.from_user

    if not is_superuser(user):
        return
    
    DIR = generate_report_course()

    document = open(DIR, "rb")
    if os.stat(DIR).st_size == 0:
        update.message.reply_text(
            no_data
        )
    else:
        update.message.reply_text(
            here
        )

        logger.info(f'User : @{user.username} requested the report of course outline')

        context.bot.send_document(
            update.message.chat_id,
            document
        )


# A function to give reports to the superuser
def report_reports(update: Update, context: CallbackContext):
    user = update.message.from_user

    if not is_superuser(user):
        return
    
    DIR = generate_reports()

    document = open(DIR, "rb")
    if os.stat(DIR).st_size == 0:
        update.message.reply_text(
            no_data
        )
    else:
        update.message.reply_text(
            here
        )

        logger.info(f'User : @{user.username} requested the list of reports made by the users')

        context.bot.send_document(
            update.message.chat_id,
            document
        )


# A function to give manage posts
def manage_posts(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(manage_posts_buttons)
    user = update.message.from_user
    if not is_admin(user) and not is_superuser(user):
        return
        
    update.message.reply_text(
        'Choose',
        reply_markup=reply_markup
    )
    
    return FIRST



# A function that manages the query of the manage posts function
def callback_handler_posts(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data == "new_post":
        if not is_admin(user) and not is_superuser(user):
            return
        user_data = context.user_data
        user_data['clicked']=[]
        keyboard = []

        for i in SCHOOL_SYSTEM:
            keyboard.append([InlineKeyboardButton(i, callback_data=i)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            choose_department,
            reply_markup= reply_markup
        )

        return REST

    elif data == 'update_post':
        query.edit_message_text(
            tell_me_code
        )
        return UPDATE
    else:
        query.edit_message_text(
            tell_me_code
        )

        return DELETE


# A function to update course outlines
def update_post(update: Update, context: CallbackContext):
    user_data = context.user_data
    course_code = update.message.text

    course = check_course(course_code)

    if course:
        update.message.reply_text(text=f'This is the current data \n {course["name"]} - {course["code"]}')
        if course['photo']:
            context.bot.send_photo(update.effective_chat.id, photo = course['file'])
        else:
            context.bot.send_document(update.effective_chat.id, course['file'])
        update.message.reply_text(
            course_insertion_message + "\n If you want to leave the name as it is, just send /skip",
            parse_mode=ParseMode.HTML
        )


        user_data['course_name'] = course['name']
        user_data['course_code'] = course['code']
        user_data['course_data'] = course['file']
        user_data['photo'] = course['photo']

       

        return UPDATE_COURSE_NAME

    else:
        update.message.reply_text(
            course_not
        )

        return UPDATE


# A function to update course outlines name
def update_name(update: Update, context: CallbackContext):
    text = update.message.text
    user_data = context.user_data

    try:
        course_code, course_description = text.split('-')
        
        course_code = course_code.replace(' ','')
        course_description = course_description.replace(' ','')
        if len(course_description)<3 or len(course_code)<3:
            update.message.reply_text(
                enter_code
            )

            return UPDATE_COURSE_NAME

        if check_course(course_code):
            
            if check_course(course_code)['code'] != user_data['course_code']:
                update.message.reply_text(
                    code_exists
                )

                return UPDATE_COURSE_NAME
        
        user_data['previous_code'] = user_data['course_code']
        user_data['course_name'] = course_description
        user_data['course_code'] = course_code
    except :
        update.message.reply_text(
                enter_code
        )
        return UPDATE_COURSE_NAME

    update.message.reply_text(
        insert_file
    )

    return UPDATE_COURSE_DATA


# A function to skip updating of course outlines name
def skip_name(update: Update, context : CallbackContext):
    user_data = context.user_data

    user_data['previous_code'] = user_data['course_code']
    update.message.reply_text(
        insert_file
    )
    
    return UPDATE_COURSE_DATA


# A function to skip updating of course outlines data
def skip_data(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    user_data['username'] = user.username
    user_data['previous_code'] = user_data['course_code']
    update.message.reply_text(
        done
    )

    save_course(user_data, user, logger)

    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END


# A function to delete course outlines
def delete_courses(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = update.message.from_user
    course_code = update.message.text
    course = check_course(course_code)
    if course:
        logger.info(f'User : @{user.username} deleted a course outline by the code of {course["code"]} and name of {course["name"]}')
        update.message.reply_text(
            deleted
        )
        delete_course(course)

    else:
        update.message.reply_text(
            course_not
        )

        return DELETE
    
    user_data = clean_user_data(user_data)
    
    return ConversationHandler.END

def logs(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_superuser(user):
        return
    
    document = open(LOGS_DIR, "rb")

    if os.stat(LOGS_DIR).st_size == 0:
        update.message.reply_text(
            no_logs
        )

    else:
        update.message.reply_text(
            here
        )

        logger.info(f'User : @{user.username} requested the logs')

        context.bot.send_document(
            update.message.chat_id,
            document
        )


# The main function of the bot.
def main():
    updater =  Updater(API)


    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(MessageHandler(Filters.regex('💬 Feedbacks'), feedbacks_list))
    dp.add_handler(MessageHandler(Filters.regex('📄 Report of courses'), report_course))
    dp.add_handler(MessageHandler(Filters.regex('📄 Reports of the users'), report_reports))
    dp.add_handler(MessageHandler(Filters.regex('📄 Logs'), logs))

    # conversation handler for searching course outline
    conv_handler_search = ConversationHandler(
        entry_points = [ MessageHandler(Filters.regex('🔎 Search'),search)],
        states = {
            FIRST:[
                CallbackQueryHandler(rest_info_search),
            ],
        },
        fallbacks=[ CommandHandler('cancel', end)]
    )

    # conversation handler for reporting
    conv_handler_report = ConversationHandler(
        entry_points=[ MessageHandler(Filters.regex('📢 Report'),report)],
        states={
            FIRST:[
                MessageHandler(Filters.text & ~Filters.command, report_data),
            ]
        },
        fallbacks=[CommandHandler('cancel',end)]

    )

    # conversation handler for telling the bot the department
    conv_handler_dept = ConversationHandler(
        entry_points=[ MessageHandler(Filters.regex('🏫 My Department'),my_dept)],
        states={
            FIRST:[
                CallbackQueryHandler(rest_dept),
            ]
        },
        fallbacks=[CommandHandler('cancel',end)]
    )

    # conversation handler for giving the recent updates
    conv_handler_recent = ConversationHandler(
        entry_points= [MessageHandler(Filters.regex('📆 Recent'), recent)],
        states={
            FIRST : [
                CallbackQueryHandler(get_course)
            ]
        },
        fallbacks=[CommandHandler('cancel', end)]
    )

    # conversation handler for giving feedback
    conv_handler_feedback = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('💬 Give us feedback'),feedback)],
        states={
            FIRST:[
                MessageHandler(Filters.text & ~(Filters.command), get_feedback)
            ]
        },
        fallbacks=[CommandHandler('cancel', end)]
    )

    # conversation handler for managing admins
    conv_handler_manage = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('🔑 Manage admins'), manage_admins)],
        states={
            FIRST:[
                CallbackQueryHandler(manage_admin_callback)
            ],
            PROMOTE:[
                MessageHandler(Filters.text & ~(Filters.command), promote)
            ],
            DEMOTE:[
                MessageHandler(Filters.text & ~(Filters.command), demote)
            ]
        },
        fallbacks=[CommandHandler('cancel', end)]
    )

    # conversation handler for giving the list of users
    conv_handler_list = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('📄 List of users'), list_of_users)],
        states={
            FIRST:[
                CallbackQueryHandler(callback_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', end)]
    )

    # conversation handler for managing
    conv_handler_post = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('📄 Manage posts'), manage_posts)
        ],
        states={
            FIRST:[
                CallbackQueryHandler(callback_handler_posts)
            ],
            COURSE_NAME: [
                MessageHandler(Filters.text & ~Filters.command, course_name)
            ],
            COURSE_DATA: [
                MessageHandler(Filters.photo, course_data_image),
                MessageHandler(Filters.document, course_data_document)
            ],
            REST: [
                CallbackQueryHandler(rest_info),
            ],
            UPDATE:[
                MessageHandler(Filters.text & ~Filters.command, update_post)
            ],
            UPDATE_COURSE_NAME:[
                MessageHandler(Filters.text & ~Filters.command, update_name),
                CommandHandler('skip', skip_name)
            ],
            UPDATE_COURSE_DATA:[
                MessageHandler(Filters.photo, course_data_image),
                MessageHandler(Filters.document, course_data_document),
                CommandHandler('skip', skip_data)
            ],
            DELETE:[
                MessageHandler(Filters.text & ~Filters.command, delete_courses)
            ]

        },
        fallbacks=[CommandHandler('cancel', end)]
    )

    dp.add_handler(conv_handler_list)
    dp.add_handler(conv_handler_manage)
    dp.add_handler(conv_handler_feedback)
    dp.add_handler(conv_handler_recent)
    dp.add_handler(conv_handler_dept)
    dp.add_handler(conv_handler_report)
    dp.add_handler(conv_handler_post)
    dp.add_handler(conv_handler_search)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()