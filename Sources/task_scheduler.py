import win32com.client
from getpass import getuser
import pathlib
import datetime

working_directory = str(pathlib.Path(__file__).parent.absolute().parent.absolute())
path_action = str(pathlib.Path(__file__).parent.absolute().parent.absolute())+"\\automatic.py"
computer_name = "" #leave all blank for current computer, current user
computer_username = ""
computer_userdomain = ""
computer_password = ""
action_id = "DriveMyFiles Task" #arbitrary action ID
action_path = path_action
action_arguments = 'python3 ' #arguments (could be something.py)
action_workdir = working_directory #working directory for action executable" 
author = getuser() #so that end users know who you are
description = "DriveMyFiles task" #so that end users can identify the task
task_id = "DriveMyFiles"
task_hidden = False #set this to True to hide the task in the interface
username = ""
password = ""
run_flags = "TASK_RUN_NO_FLAGS" #see dict below, use in combo with username/password

#define constants
TASK_TRIGGER_TIME = 1
TASK_CREATE = 2
TASK_CREATE_OR_UPDATE = 6
TASK_ACTION_EXEC = 0
IID_ITask = "{148BD524-A2AB-11CE-B11F-00AA00530503}"
RUNFLAGSENUM = {
    "TASK_RUN_NO_FLAGS"              : 0,
    "TASK_RUN_AS_SELF"               : 1,
    "TASK_RUN_IGNORE_CONSTRAINTS"    : 2,
    "TASK_RUN_USE_SESSION_ID"        : 4,
    "TASK_RUN_USER_SID"              : 8 
}

def run_task(hour,day,week):
    #connect to the scheduler (Vista/Server 2008 and above only)
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect(computer_name or None, computer_username or None, computer_userdomain or None, computer_password or None)
    rootFolder = scheduler.GetFolder("\\")

    start_time = datetime.datetime.now() + datetime.timedelta(hours=hour, days=day, weeks= week)
    taskDef = scheduler.NewTask(0)
    colTriggers = taskDef.Triggers
    trigger = colTriggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = start_time.isoformat()
    trigger.Enabled = True

    colActions = taskDef.Actions
    action = colActions.Create(TASK_ACTION_EXEC)
    action.ID = action_id
    action.Path = action_path
    action.WorkingDirectory = action_workdir
    action.Arguments = action_arguments

    info = taskDef.RegistrationInfo
    info.Author = author
    info.Description = description

    settings = taskDef.Settings
    settings.Enabled = False
    settings.Hidden = task_hidden

    #register the task (create or update, just keep the task name the same)
    result = rootFolder.RegisterTaskDefinition(task_id, taskDef, TASK_CREATE_OR_UPDATE, "", "", RUNFLAGSENUM[run_flags] ) #username, password

    #run the task once
    task = rootFolder.GetTask(task_id)
    task.Enabled = True
    runningTask = task.Run("")