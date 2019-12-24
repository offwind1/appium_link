
"""
@author: hyt
@time：2019-03-27
"""


class Action(object):

    def __init__(self, name):
        self.name = name

    def click(self):
        print(self.name, "click")

action_list = [Action("one"), Action("two")]

# def click():
#     action.click()

code = """
from test1 import *

# print(action)
# action.click()

set_action(action)
click()
print(action.__name__)

"""

for action in action_list:
    try:
        exec(compile(code.encode("utf-8"), '<string>', 'exec'),{"action":action})
    except Exception as e:
        raise e
    


