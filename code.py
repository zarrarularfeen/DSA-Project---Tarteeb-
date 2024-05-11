from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from datetime import datetime, date
import sys
import numpy as np

# <------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------> #

tasks = [] # used to store task information 
temp_tasks = [] # used temporarily to make a Segment Tree to find Max priority.
tasks_per_day = {} # used to calculate segmentation using dates provided by user.
tasks_length = len(tasks) # length of tasks

min_date = None # lower limit of range for forming tasks list.
max_date = None # upper limit of range for forming tasks list.

segment_tree_max = [] # segment tree which is used to find minimum priority in a given segmentation
segment_tree_min = [] # segment tree which is used to find maximum priority in a given segmentation

# <------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------> #

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("main.ui", self)
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)      # connect the calendar to the function
        self.calendarDateChanged()                                                  # call the function to return the date selected at the first instance
        self.saveButton.clicked.connect(self.saveChanges)                           # if button pressed call the function
        self.addButton.clicked.connect(self.addNewTask)                             # if button pressed call the function
        self.deleteButton.clicked.connect(self.deleteNewTask)                       # if button pressed call the function
        self.viewTaskButton.clicked.connect(self.viewTaskNewTask)                   # if button pressed call the function
        self.to_dd = self.findChild(QtWidgets.QComboBox, "to_dd")
        self.to_mm = self.findChild(QtWidgets.QComboBox, "to_mm")
        self.to_yyyy = self.findChild(QtWidgets.QComboBox, "to_yyyy")


    def calendarDateChanged(self):
        print("The calendar date was changed.")                                     # print when the date is changed
        dateSelected = self.calendarWidget.selectedDate().toPyDate()                # extract the date selected
        print("Date selected - ", dateSelected)                                     # print the date selected
        print()
        self.updateTaskList(dateSelected)                                           # update the ListWidget for the date selected
        

    def updateTaskList(self, date):
        self.tasksListWidget.clear()                                          # clears previous data to refresh current information in the task list
        for task in tasks:                                                    # adding the tasks to the list widget
            if task[2] == date.strftime(r'%Y-%m-%d'):                         # checking to coordinate task date and current date selected
                item = QListWidgetItem(task[0] + " | " + str(task[1]))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)   # checks the status of the task by user
                if task[3] == "YES":
                    item.setCheckState(QtCore.Qt.Checked)
                elif task[3] == "NO":
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.tasksListWidget.addItem(item)                            # adds the task to the listwidget


    def saveChanges(self):
        name = str(self.taskLineEdit.text())
        prio = self.priorityComboBox.currentText()
        for i in range(self.tasksListWidget.count()): # iterating through present items shown to the user
            item = self.tasksListWidget.item(i)
            task = item.text()
            task = task.split('|')
            task_name = task[0].strip()
            priority = task[1].strip()
            date = self.calendarWidget.selectedDate().toPyDate()

            if name == task_name: # updates information of existing task
                if item.checkState() == QtCore.Qt.Checked: # checks the status of tasks input by user using checkbox and updates accordingly
                    flag = update_task(name, int(prio), date, 'YES')
                else:
                    flag = update_task(name, int(prio), date, 'NO')
            else:
                if item.checkState() == QtCore.Qt.Checked: # checks the status of tasks input by user using checkbox and updates accordingly
                    flag = update_task(task_name, int(priority), date, 'YES')
                else:
                    flag = update_task(task_name, int(priority), date, 'NO')
        print('Tasks - ' , tasks)
        print()
        self.updateTaskList(date) 
        self.taskLineEdit.clear()


        # show a message box to show that the changes have been saved
        if flag == True:
            messageBox = QMessageBox()
            messageBox.setText("Changes Saved.")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()
        elif flag == False:
            messageBox = QMessageBox()
            messageBox.setText("This Task does not Exist.")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()
    

    def addNewTask(self):
        task_name = str(self.taskLineEdit.text())                           # get the task from the line edit
        date = self.calendarWidget.selectedDate().toPyDate()
        priority = self.priorityComboBox.currentText()                      # get the priority from the combo box
        flag = add_task(task_name, int(priority), date, "NO")               # add the task to the list
        print('Tasks - ' , tasks)
        print()
        self.updateTaskList(date)                                           # update the task list
        self.taskLineEdit.clear()                                           # clear the line edit after adding the task


        # show a message box to show that the changes have been saved
        if flag == True:
            messageBox = QMessageBox()
            messageBox.setText("Cannot Add Duplicate Task")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()
        elif flag == False:
            messageBox = QMessageBox()
            messageBox.setText("Select a Date Onwards of " + (date.today().strftime(r'%Y-%m-%d')))
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()
        else:
            messageBox = QMessageBox()
            messageBox.setText("Task Succesfully Added")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()


    def deleteNewTask(self):
        task_name = str(self.taskLineEdit.text())                           # get the task from the line edit
        date = self.calendarWidget.selectedDate().toPyDate()                
        flag = delete_task(task_name, date)                                 # delete the task in the list    
        print('Tasks - ' , tasks)
        print()
        self.updateTaskList(date)                                           # update the task list
        self.taskLineEdit.clear()                                           # clear the line edit after adding the task

        # show a message box to show that the changes have been saved
        if flag == True:
            messageBox = QMessageBox()
            messageBox.setText("Task deleted.")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()
        elif flag == False:
            messageBox = QMessageBox()
            messageBox.setText("This Task does not Exist.")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()


    def viewTaskNewTask(self):
        # extracting the range selected by user
        from_dd = self.from_dd.currentText()
        from_mm = self.from_mm.currentText()
        from_yyyy = self.from_yyyy.currentText()

        to_dd = self.to_dd.currentText()
        to_mm = self.to_mm.currentText()
        to_yyyy = self.to_yyyy.currentText()
        option = self.sortByComboBox.currentText()

        # formatting the input for function arguments
        if len(to_dd) == 1:
            to_dd = '0' + to_dd
        
        if len(from_dd) == 1:
            from_dd = '0' + from_dd

        monthly_mapping = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':11, 'Dec':12}

        start_date =  from_yyyy + '-' +  monthly_mapping[from_mm] + '-' + from_dd 
        end_date = to_yyyy + '-' +  monthly_mapping[to_mm] + '-' + to_dd 


        view_lst = view_task(start_date, end_date, option)                       # getting the corresponding tasks according to option chosen
        self.tasksListWidget.clear()
        for task in view_lst:                                                    # adding the tasks to the list widget
            item = QListWidgetItem(task[0] + " | " + str(task[1]) + " | " + task[2])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if task[3] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif task[3] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasksListWidget.addItem(item)

# <------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------> #

def build_tree_min(lst, length):
    segment_tree = [('', float('inf'), '', '')] * (2 ** int(np.log2(2 * length - 1) + 1)) # declaration of base structure and total nodes calculated using a formula.
    for i in range(length):
        update_tree_min(length, segment_tree, i, lst[i]) # iterating through the task list and updating relevant nodes to form the segment tree for minimum.
    return segment_tree


def build_tree_max(lst, length):
    segment_tree = [('', 0, '', '')] * (2 ** int(np.log2(2 * length - 1) + 1)) # declaration of base structure and total nodes calculated using a formula.
    for i in range(length):
        update_tree_max(length, segment_tree, i, lst[i]) # iterating through the task list and updating relevant nodes to form the segment tree for maximum.
    return segment_tree


def update_tree_min(length, segment_tree, index, value):
    def inner(current_node, left, right):
        if index < left or index > right: # stop if limit ends are out of the segmentation provided.
            return
        if left == right: # Updates value when finds the leaf node.
            segment_tree[current_node] = value
            return
        mid = (left + right) // 2 # calculating the midpoint of the segmentation ends.
        inner(2 * current_node + 1, left, mid) # recursively updating the left child of the corresponding node.
        inner(2 * current_node + 2, mid + 1, right) # recursively updating the right child of the corresponding node.

        # calculating the node values depending on its children, in this case we want the minimum value.
        if segment_tree[2 * current_node + 1][1] <= segment_tree[2 * current_node + 2][1]:
            segment_tree[current_node] = segment_tree[2 * current_node + 1] # for left child
        else:
            segment_tree[current_node] = segment_tree[2 * current_node + 2] # for right child
    inner(0, 0, length - 1)


def update_tree_max(length, segment_tree, index, value):
    def inner(current_node, left, right): 
        if index < left or index > right: # stop if limit ends are out of the segmentation provided.
            return
        if left == right:
            segment_tree[current_node] = value # Updates value when finds the leaf node.
            return
        mid = (left + right) // 2 # calculating the midpoint of the segmentation ends.
        inner(2 * current_node + 1, left, mid) # recursively updating the left child of the corresponding node.
        inner(2 * current_node + 2, mid + 1, right) # recursively updating the right child of the corresponding node.

        # calculating the node values depending on its children, in this case we want the minimum value.
        if segment_tree[2 * current_node + 1][1] >= segment_tree[2 * current_node + 2][1]:
            segment_tree[current_node] = segment_tree[2 * current_node + 1] # for left child
        else:
            segment_tree[current_node] = segment_tree[2 * current_node + 2] # for right child
    inner(0, 0, length - 1)


def query_tree_min(length, segment_tree, start, end):
    def inner(current_node, left, right):
        if right < start or left > end: # If the current segment is outside the query range, return a dummy value
            return ('', 0)
        if start <= left and right <= end:  # If the current segment is inside the query range, return the value of the current node
            return segment_tree[current_node]
        mid = (left + right) // 2 # calculating midpoint of the segmentation ends.
        l = inner(2 * current_node + 1, left, mid) # recursively query the left child of the corresponding node.
        r = inner(2 * current_node + 2, mid + 1, right) # recursively query the right child of the corresponding node.

        # Return the minimum value of the two children
        if l[1] <= r[1]:
            return l # left child
        else:
            return r # right child
    return inner(0, 0, length - 1)


def query_tree_max(length, segment_tree, start, end):
    def inner(current_node, left, right):
        if right < start or left > end: # If the current segment is outside the query range, return a dummy value
            return ('', 0)
        if start <= left and right <= end: # If the current segment is inside the query range, return the value of the current node
            return segment_tree[current_node]
        mid = (left + right) // 2 # calculating midpoint of the segmentation ends.
        l = inner(2 * current_node + 1, left, mid) # recursively query the left child of the corresponding node.
        r = inner(2 * current_node + 2, mid + 1, right) # recursively query the right child of the corresponding node.

        # Return the maximum value of the two children
        if l[1] >= r[1]:
            return l # left child
        else:
            return r # right child
    return inner(0, 0, length - 1)

# <------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------> #

def add_task(task, priority, date, status):
    global tasks,temp_tasks, tasks_length, tasks_per_day, segment_tree_max, segment_tree_min, min_date, max_date

    if date.today() > date:
        return False

    if min_date == None: # Task list empty
        min_date = date # setting lower bound
        max_date = date # setting upper bound
        difference = (max_date - min_date).days + 1 # calculating amount of days

        tasks = [('', float('inf'), '', '')] * (10 * difference) 
        temp_tasks = [('', 0, '', '')] * (10 * difference)

        if date.strftime(r'%Y-%m-%d') not in tasks_per_day: # If task date added for first time
            tasks_per_day[date.strftime(r'%Y-%m-%d')] = 0
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] + ((difference - 1) * 10)
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        elif tasks_per_day[date.strftime(r'%Y-%m-%d')] < 10: # maximum tasks per day can be 10
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] + ((difference - 1) * 10)
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        else:
            print('Maximum Tasks for the Day.')


    elif min_date <= date and max_date >= date: # date exist between the lower and upper bound
        temp_date = date
        difference = (temp_date - min_date).days

        for val in range(0, tasks_length):
            if task.lower() == tasks[val][0].lower():
                return True

        if date.strftime(r'%Y-%m-%d') not in tasks_per_day:
            tasks_per_day[date.strftime(r'%Y-%m-%d')] = 0
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] + ((difference) * 10)
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        elif tasks_per_day[date.strftime(r'%Y-%m-%d')] < 10:
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] + ((difference) * 10)
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        else:
            print('Maximum Tasks for the Day.')

    elif date < min_date: # new lower bound will be defined
        temp_date = date
        difference = (min_date - temp_date).days

        tasks = [('', float('inf'), '', '')] * (10 * difference) + tasks
        temp_tasks = [('', 0, '', '')] * (10 * difference) + temp_tasks

        if date.strftime(r'%Y-%m-%d') not in tasks_per_day:
            tasks_per_day[date.strftime(r'%Y-%m-%d')] = 0
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')]
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        elif tasks_per_day[date.strftime(r'%Y-%m-%d')] < 10:
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')]
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        else:
            print('Maximum Tasks for the Day.')

        min_date = date

    elif date > max_date: # new upper bound will be defined
        temp_date = date
        difference = (temp_date - max_date).days

        tasks = tasks + [('', float('inf'), '', '')] * (10 * difference)
        temp_tasks = temp_tasks + [('', 0, '', '')] * (10 * difference)
        
        if date.strftime(r'%Y-%m-%d') not in tasks_per_day:
            tasks_per_day[date.strftime(r'%Y-%m-%d')] = 0
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] - 10
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        elif tasks_per_day[date.strftime(r'%Y-%m-%d')] < 10:
            index = tasks_per_day[date.strftime(r'%Y-%m-%d')] - 10
            tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[index] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            tasks_per_day[date.strftime(r'%Y-%m-%d')] += 1
        else:
            print('Maximum Tasks for the Day.')
        
        max_date = date
    
    tasks_length = len(tasks)

    segment_tree_max = build_tree_max(temp_tasks, tasks_length)
    segment_tree_min = build_tree_min(tasks, tasks_length)


def update_task(task, priority, date, status):
    global tasks,temp_tasks, tasks_length, tasks_per_day, segment_tree_max, segment_tree_min, min_date, max_date 

    for val in range(tasks_length): # iterating to find task in tasks list
        d = tasks[val][2]
        if tasks[val][0].lower().strip() == task.lower().strip() and d == date.strftime(r'%Y-%m-%d'): # finding correct position adn updating values
            tasks[val] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            temp_tasks[val] = (task, priority, date.strftime(r'%Y-%m-%d'), status)
            update_tree_max(tasks_length, segment_tree_max, val, temp_tasks[val])
            update_tree_min(tasks_length, segment_tree_min, val, tasks[val])
            return True
    return False


def delete_task(task, date):
    global tasks,temp_tasks, tasks_length, tasks_per_day, segment_tree_max, segment_tree_min, min_date, max_date 

    date = date.strftime(r'%Y-%m-%d')
    flag = False

    for val in range(tasks_length): # iterating to find the task
        d = tasks[val][2]
        if tasks[val][0].lower().strip() == task.lower().strip() and d == date: # finding the correct position and initializing it once again
            tasks_per_day[date] -= 1

            tasks[val] = ('', float('inf'), '', '')
            temp_tasks[val] = ('', 0, '', '')
            flag = True
            break
    
    if flag == True:
        # following are formulas made to calibrate the deletion of tasks so that there is no override when adding new ones
        tasks = tasks[:val] + tasks[val + 1:val + tasks_per_day[date] + 1] + tasks[val + tasks_per_day[date] + 1:val + tasks_per_day[date] + 1 + 10 - tasks_per_day[date]] + [('', float('inf'), '', '')] + tasks[val + tasks_per_day[date] + 1 + 10 - tasks_per_day[date] + 1:]
        temp_tasks = temp_tasks[:val] + temp_tasks[val + 1:val + tasks_per_day[date] + 1] + temp_tasks[val + tasks_per_day[date] + 1:val + tasks_per_day[date] + 1 + 10 - tasks_per_day[date]] + [('', 0, '', '')] + temp_tasks[val + tasks_per_day[date] + 1 + 10 - tasks_per_day[date] + 1:]
        tasks_length = len(tasks)

        # update_tree_max(tasks_length, segment_tree_max, val, ('', float('inf'), '', ''))
        # update_tree_min(tasks_length, segment_tree_min, val, ('', 0, '', ''))

        segment_tree_max = build_tree_max(temp_tasks, tasks_length)
        segment_tree_min = build_tree_min(tasks, tasks_length)

        # print(segment_tree_max)

        # print(segment_tree_min)
    
    return flag


def view_task(start_date, end_date, option):
    global tasks, tasks_length, tasks_per_day, segment_tree_max, segment_tree_min, min_date, max_date 

    # formatting the following variables
    view_lst = []
    option = option.strip()

    start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    end_date = datetime.strptime(end_date, r'%Y-%m-%d')

    if option == 'All Tasks In This Range':
        for task in tasks: # iterating throught the task list
            if task[2] != '':
                d = task[2]
                d = datetime.strptime(d, r'%Y-%m-%d')
                if start_date <= d <= end_date:
                    view_lst.append(task)

    elif option == 'Completed Tasks':
        for task in tasks: # iterating throught the task list to find completed 
            if task[2] != '':
                d = datetime.strptime(task[2], r'%Y-%m-%d')
                if start_date <= d <= end_date and task[3] == 'YES':
                    view_lst.append(task)

    elif option == 'Incomplete Tasks':
        for task in tasks: # iterating throught the task list to find uncompleted 
            if task[2] != '':
                d = datetime.strptime(task[2], r'%Y-%m-%d')
                if start_date <= d <= end_date and task[3] != 'YES':
                    view_lst.append(task)

    elif option == 'Minimum Priority Task In This Range':
        # following are different cases of the range given by user and how to calculate their respective indexes
        if start_date.date() >= min_date and end_date.date() <= max_date:
            start_date = (min_date - start_date).days * 10
            end_date = tasks_length - 1 - ((max_date - end_date).days * 10)
        elif start_date.date() <= min_date and end_date.date() >= max_date:
            start_date = 0
            end_date = tasks_length - 1
        elif start_date.date() <= min_date and end_date.date() <= max_date:
            start_date = 0
            end_date = tasks_length - 1 - ((max_date - end_date).days * 10)
        elif start_date.date() >= min_date and end_date.date() >= max_date:
            start_date = (min_date - start_date).days * 10
            end_date = tasks_length - 1    
        
        min_priority_task = query_tree_min(tasks_length, segment_tree_min, start_date, end_date)
        view_lst.append(min_priority_task)

    elif option == 'Maximum Priority Task In This Range':
        # following are different cases of the range given by user and how to calculate their respective indexes
        if start_date.date() >= min_date and end_date.date() <= max_date:
            start_date = (min_date - start_date).days * 10
            end_date = tasks_length - 1 - ((max_date - end_date).days * 10)
        elif start_date.date() <= min_date and end_date.date() >= max_date:
            start_date = 0
            end_date = tasks_length - 1
        elif start_date.date() <= min_date and end_date.date() <= max_date:
            start_date = 0
            end_date = tasks_length - 1 - ((max_date - end_date).days * 10)
        elif start_date.date() >= min_date and end_date.date() >= max_date:
            start_date = (min_date - start_date).days * 10
            end_date = tasks_length - 1  

        max_priority_task = query_tree_max(tasks_length, segment_tree_max, start_date, end_date)
        view_lst.append(max_priority_task)

    return view_lst

# <------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------> #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window() 
    window.show() 
    sys.exit(app.exec())