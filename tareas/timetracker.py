import os
import string
from datetime import datetime

#TODO: edit_logbook() ?

def logbook2shptime(project, note, start_time, end_time):
    if not project:
        project = 'Otros' # project by default
    return f'shptime --dry-run add -n {project} -t "{note}" -s { start_time.isoformat() } -e { end_time.isoformat() }'

def push_commit(commit_file):
    #TODO: improve exceptions handling
    try:
        os.system(f"sh {commit_file}") #TODO: bash? sh?
        os.system(f"rm {commit_file}")
    except Exception:
        print("[-] error")

def alias_from_text(text):
    aliases = [
        ''.join(c for c in word if c not in string.punctuation.replace("-",""))
    # ^^ filter every punctuation symbol except "-" (an alias may contain it) ^^
         for word in text.split() if word.startswith("#")
    ]
    if len(aliases)>0:
        return aliases[0]
    else:
        return False

def edit_commit(dtime, logbook_file):
    actions = []
    commit_file = "commit.tmp"
    with open(logbook_file,"r+") as f:
        for line in reversed( f.read().splitlines() ): # reading from most recent lines
            if not line.startswith('--committed'): # 1. get actions until "--commited--" line found:
                actions.append(line)
            else:
                if len(actions)>0:                   # 2. dump actions on commit_file, edit it and push it:
                    with open(commit_file,"w") as cf:
                        start_time = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0) #TODO? use "mark" or my own start/end marks ?
                        for action in actions:
                            arr_action = action.replace('"',"'").replace('`',"'").split(',') #TODO: load from csv and strip quotes properly
                            note = arr_action[1]
                            project = alias_from_text(note)
                            end_time = datetime.strptime(arr_action[0], '%Y-%m-%dT%H:%M:%S')
                            cf.write(f"{ logbook2shptime( project, note, start_time, end_time ) }\n")
                            start_time = end_time # so next action starts on the end_time of this action
                    os.system( "vim {}".format(commit_file) )
                    #os.system( "edit {0} || vim {0}".format(commit_file) ) #TODO: what's the best way of chooosing user's preferred editor?
                    push_commit(commit_file)
                    f.write(f"--committed on { dtime.isoformat() } until here--\n")
                else:
                    print("[-] nada para hacer commit")
                break

def prompt_commands():
    try:
        from prompt_toolkit.completion import FuzzyWordCompleter
        from prompt_toolkit.shortcuts import prompt
        commands = FuzzyWordCompleter(["/commit"])
        opt = prompt(">> ", completer=commands, complete_while_typing=True)
        return opt
    except ImportError:
        raise ImportError

def complete_commands():
    import readline
    commands = ["/commit"]
    def completer(text, i):
        command = [c for c in commands if c.startswith(text)]
        try:
            return command[i]
        except IndexError:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('') # so '/' insde commands works correctly
    opt = input(">>> ")
    return opt
