from datetime import datetime
from typing import Dict

from datetime import datetime
from plugins.connection import *
from .keyboards import generate_keyboard
from .Settings import SuperUser


# Used this to create a document of the course outlines.
def document_creator(user_data: Dict):
    try:
        clicked = user_data['clicked']
        try:
            new_document = {
                'name' : user_data['course_name'],
                'code' : user_data['course_code'],
                'file' : user_data['course_data'],
                'division':clicked[0]
            }
        except:
            new_document={
                'division':clicked[0]
            }
        if clicked[0]=='Applied':
            if len(clicked)==3:
                new_document['year']=int(clicked[1][0])
                new_document['semester']=clicked[2]
                new_document['department'] = None
                new_document['school'] = None
            else:
                new_document['year']=int(clicked[2][0])
                new_document['semester']=clicked[3]
        elif clicked[0]=="Fresh":
            new_document['semester'] = clicked[1]
            new_document['year'] = 1
            new_document['department'] = None
            new_document['school'] = None
        else:
            if len(clicked)==4:
                new_document['year']=int(clicked[2][0])
                new_document['semester']=clicked[3]
                new_document['department'] = None
                new_document['school'] = clicked[1]
            else:
                new_document['department']= clicked[2]
                new_document['year']=int(clicked[3][0])
                new_document['semester']=clicked[4]
                new_document['school'] = clicked[1]

        new_document['visible'] = True
    except:
        new_document = {
            'name' : user_data['course_name'],
            'code' : user_data['course_code'],
            'file' : user_data['course_data'],
            'photo' : user_data['photo']

        }

    return new_document



# Used this to find users from the database.
def find_user(id = None, username = None):
    if id:
        user = users.find_one(
            {
                'id':id
                }
        )
    else:
        user = users.find_one({
            'username':{
                "$regex":username,
                '$options':'i'
            }
        }
        )


    return user



# Used this to save the course outline.
def save_course(user_data : Dict[str,str], user=None, logger = None):
    if "previous_code" in user_data:
        course = check_course(user_data['previous_code'])
    else:
        course = None

    if course:
        set_new = {
            '$set':{
                'name': user_data['course_name'],
                'code': user_data['course_code'],
                'photo': user_data['photo'],
                'file': user_data['course_data']
            }
        }

        logger.info(f'User : @{user.username} updated course outline with the previous code of {user_data["previous_code"]} to the course code of {user_data["course_code"]} and name of {user_data["course_name"]}')

        course_outlines.update_one(course, set_new)
    else:
        photo = user_data['photo']
        new_document = document_creator(user_data)
        new_document['photo'] = photo
        new_document['date_added'] = datetime.utcnow()
        new_document['uploaded_by'] = user_data['username']
        new_document['downloads'] = 0
        course_outlines.insert_one(new_document)

        logger.info(f'User : @{user.username} saved a new course outline by the code of {user_data["course_code"]} and name of {user_data["course_name"]}')
    
    user_data.clear()



# Used this to save the user.
def save_user(user):
    userInfo = {
        'id': user.id,
        'username':user.username,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'started_at': datetime.now(),
        'admin':False,
    }

    users.insert_one(userInfo)



# Used this to save the report of the user.
def save_report(user_data: Dict[str, str]):
    new_report = {
        'reporter': user_data['username'],
        'report': user_data['report'],
        'date': datetime.now()
    }
    user_data.clear()

    reports.insert_one(new_report)



# Used this to save the department of the user.
def save_dept(clicked, user):
    if clicked[0] == 'Fresh':
        document={
            "$set":{
                "division" : "Fresh",
                "year":1,
                "school":None,
                "department":None,
            }
        }
    elif clicked[0] == 'Applied':
        if len(clicked) == 2:
            document={
                "$set":{
                    "division" : "Applied",
                    "year":2,
                    "school":None,
                    "department":None,
                }
            }
        else:
            document={
                "$set":{
                    "department" : "Applied",
                    "division":clicked[1],
                    "year":int(clicked[2][0]),
                    "school":None,
                }
            }
    else:
        if len(clicked)==3:
            document={
                "$set":{
                    "department" : "Engineering",
                    "school":clicked[1],
                    "year":int(clicked[2][0]),
                    "division":None,
                }
            }
        else:
            document={
                "$set":{
                    "division" : "Engineering",
                    "school":clicked[1],
                    "department":clicked[2],
                    "year":int(clicked[3][0])
                }
            }
    
    current_user = find_user(user.id)
    
    users.update_one(current_user, document)



# Used this to list all of the courses in the database.
def list_all_courses():
    fetched_courses = list(course_outlines.find({
        "visible":True
    }))
    courses = {}
    for element in fetched_courses:
        courses[f"{element['name']} - {element['code']}"]= [element['file'], element['photo']]
    
    return courses

# Get the users department and year to fetch the course outline related to the user.
def get_recent(user):
    user = users.find_one({
        "id":user['id']
    })
    # get the current datetime
    now = datetime.now()
    try:
        year = user['year']
        dept = user['department']
        school = user['school']
        division = user['division']

        courses = course_outlines.find({
            'year': year,
            'department': dept ,
            'school':school,
            'division':division,
            "date_added":{
                # fetch the data to the past two days.
                "$gt":datetime(now.year, now.month, now.day -1)
                },
            "visible": True
        })
        keyboard = generate_keyboard(list(courses))
        return keyboard
    except:
        return False

# A method to check if the user has already started the bot
def check_user(user_id):
    user = users.find_one({"id":user_id})
    if user:
        return True
    else:
        return False


# A method to check if the course already exists.
def check_course(code):
    course = course_outlines.find_one({
        "code":{
            "$regex":code,
            '$options':'i'
            },
        "visible":True
        }
    )
    if course:
        return course
    else:
        return False

    
# A method to check the current department of the user.
def check_dept(user_id):
    user = users.find_one({
        "id" : user_id
    })
    try:
        info = {
            'department':user['department'],
            'division':user['division'],
            'year': user['year'],
            'school': user['school']
        }

        return info
    except:
        return {}

# Used to fetch the course from the database
def fetch_course(course_code):
    course = course_outlines.find_one(
        {
            "code": course_code,
            "visible":True
        }
    )

    return course


# A function used to store the feedback of the users.
def save_feedback(user, feedback):
    document = {
        'user':user.id,
        'username': user.username,
        'feedback': feedback,
        'date': datetime.now()
    }

    feedbacks.insert_one(document)



# checks if the user is admin or not.
def is_admin(user = None, username = None):
    
    if user:
        if user.username == SuperUser:
            return True
        user = users.find_one({
            'id':user.id,
        })

    else:
        if username == SuperUser:
            return True
        user = users.find_one({
            'username':{
                "$regex":username,
                '$options':'i'
            }
        })
    
    if user:
        if user['admin']:
            return True
        else:
            return False
    else:
        return False
    
# checks if the user is admin or not.
def is_superuser(user = None, username = None):
    if user:
        if user.username in SuperUser:
            return True
        else:
            return False
    else:
        if username in SuperUser:
            return True
        else:
            return False


def list_users():
    user_list = users.find(
        {
            'admin':False
        }
    )

    users_list = []
    for user in user_list:
        users_list.append(user['username'])
    users_list.sort()
    return users_list

def list_admins():
    user_list = users.find(
        {
            'admin':True
        }
    )
    users_list = []
    for user in user_list:
        users_list.append(user['username'])
    users_list.sort()
    return users_list

def make_admin(username):
    user = users.find_one({
        'username':{
            "$regex":username,
            '$options':'i'
        }
    })

    set_admin = {
        "$set":{
            'admin':True
        }   
    }

    users.update_one(user, set_admin)
    
    return user['id']

def make_not_admin(username):
    user = users.find_one({
        'username':{
            "$regex":username,
            '$options':'i'
        }
    })

    set_not_admin = {
        "$set":{
            'admin':False
        }   
    }

    users.update_one(user, set_not_admin)
    
    return user['id']


def delete_course(course):
    set_value = {
        "$set":{
            'visible':False,
            'deleted_date':datetime.now()
        }
    }

    course_outlines.update_one(course, set_value)

def clean_user_data(user_data):
    return user_data.clear()