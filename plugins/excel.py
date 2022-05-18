from asyncore import write
import os
import csv
from datetime import datetime
from .connection import *
from .Settings import FILE_DIR


save_path = FILE_DIR + "csv files"


def generate_file():
    myquery = users.find()

    file = f'users_list_{datetime.now().strftime("%Y%m%d %H-%M-%S")}.csv'.replace(' ',"_")
    complete_path = os.path.join(save_path, file)

    writer(myquery, complete_path)
    return complete_path



def generate_file_admins():
    myquery = users.find({
        'admin':True
    })

    file = f'admins_list_{datetime.now().strftime("%Y%m%d %H-%M-%S")}.csv'.replace(' ',"_")
    complete_path = os.path.join(save_path, file)
    writer(myquery, complete_path)

    return complete_path


def generate_reports():
    myquery = reports.find()

    file = f'reports_list_{datetime.now().strftime("%Y%m%d %H-%M-%S")}.csv'.replace(' ',"_")
    complete_path = os.path.join(save_path, file)
    writer_report(myquery, complete_path)

    return complete_path

def generate_feedbacks():
    myquery = feedbacks.find()

    file = f'feedbacks_list_{datetime.now().strftime("%Y%m%d %H-%M-%S")}.csv'.replace(' ',"_")
    complete_path = os.path.join(save_path, file)
    writer_feedback(myquery, complete_path)

    return complete_path



def generate_report_course():
    myquery = course_outlines.find()

    file = f'course_report_list_{datetime.now().strftime("%Y%m%d %H-%M-%S")}.csv'.replace(' ',"_")
    complete_path = os.path.join(save_path, file)

    writer_report_course(myquery, complete_path)

    return complete_path



def writer(query, path):
    output = csv.writer(open(path, 'wt'))

    for items in query:
        a = list([items['username'], f';     Started at {items["started_at"]}'])
        output.writerow(a)


def writer_report (query, path):
    output = csv.writer(open(path, 'wt'))

    for items in query:
        a = list([items['reporter'], f';     Reported at {items["date"]}', [f"Reported that {items['report']} is missing"]])
        output.writerow(a)

def writer_report_course (query, path):
    output = csv.writer(open(path, 'wt'))

    for items in query:
        a = list([items['uploaded_by']], f';     Uploaded {items["code"]} - {items["name"]} at {items["date_added"]} and have {items["downloads"]} downloads')
        output.writerow(a)

def writer_feedback(query, path):
    output = csv.writer(open(path, 'wt'))

    for items in query:
        a = list([items['username'], f';     Said {items["feedback"]}', [f" on {items['date']}"]])
        output.writerow(a)