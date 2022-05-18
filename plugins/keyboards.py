from telegram import *

# Buttons displayed for the normal users.
normal_buttons = [['🔎 Search'],['📆 Recent','📢 Report'],['🏫 My Department'],['💬 Give us feedback']]

# Buttons displayed for the admin users.
admin_buttons = [['📄 Manage posts','💬 Feedbacks'],['📄 Reports of the users']]

# Buttons displayed fot the superadmin users.
superadmin_buttons = [['🔑 Manage admins','📄 List of users'],['📄 Report of courses'],['📄 Logs']]


# Inline buttons displayed for the admin users.
manage_admins_buttons = [
    [
        InlineKeyboardButton(text = '🎖️ Promote to admins',callback_data='promote'),
        InlineKeyboardButton(text = '⬇️ Demote Admins',callback_data='demote'),
    ]
]


# Inline buttons displayed for the post method.
manage_posts_buttons = [
    
    [InlineKeyboardButton(text = '🆕 New Post',callback_data='new_post')],
    [InlineKeyboardButton(text = '🆕 Update Post',callback_data='update_post')],
    [InlineKeyboardButton(text = '❌ Delete Post',callback_data='delete_post')],
    
]

def generate_keyboard(courses):
    keyboard = []

    for item in courses:
        keyboard.append([InlineKeyboardButton(f"{item['name']} - {item['code']}", callback_data = item['code'])])
    keyboard.append([InlineKeyboardButton('Cancel', callback_data='cancel')])

    return keyboard