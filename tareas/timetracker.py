import os
import string
from datetime import datetime

def register2shptime(project, note, start_time, end_time):
    if not project:
        project = 'Otros' # project by default
    return f'shptime --dry-run add -n {project} -t "{note}" -s { start_time.isoformat() } -e { end_time.isoformat() }'

def push_commit():
    #TODO: may improve exceptions handling
    try:
        os.system("sh commit.tmp")
        os.system("rm commit.tmp")
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

def edit_commit(dtime, register_file):
    #WIP: get intervals from intervals.template
    #     and use them to define start_time/end_time when applicable
    actions = []
    with open(register_file,"r+") as f:
        for line in reversed( f.read().splitlines() ): # reading from most recent lines
            if not line.startswith('--committed'): # 1. get actions until "--commited--" line found:
                actions.append(line)
            else:
                if len(actions)>0:                   # 2. dump actions on 'commit.tmp', edit it and push it:
                    with open('commit.tmp',"w") as cf:
                        start_time = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)
                        for action in reversed(actions): # actions have been added from newest to oldest,
                                                         # so now will be dumped to 'commit.tmp' in chronological order (from newest to oldest)
                            arr_action = action.replace('"',"'").replace('`',"'").split(',') #TODO: load from csv and strip quotes properly
                            note = arr_action[1]
                            project = alias_from_text(note)
                            end_time = datetime.strptime(arr_action[0], '%Y-%m-%dT%H:%M:%S')
                            cf.write(f"{ register2shptime( project, note, start_time, end_time ) }\n")
                            start_time = end_time # so next action starts on the end_time of this action
                    os.system( "editor commit.tmp" )
                    push_commit()
                    f.write(f"--committed on { dtime.isoformat() } until here--\n")
                else:
                    print("[-] nada para hacer commit")
                break

def prompt_commands():
    try:
        from prompt_toolkit.completion import FuzzyWordCompleter
        from prompt_toolkit.shortcuts import prompt
        commands = FuzzyWordCompleter(["/commit", "/intervalos", "/registro"])
        opt = prompt(">> ", completer=commands, complete_while_typing=True)
        return opt
    except ImportError:
        raise ImportError

def complete_commands():
    import readline
    commands = ["/commit", "/intervalos", "/registro"]
    def completer(text, i):
        command = [c for c in commands if c.startswith(text)]
        try:
            return command[i]
        except IndexError:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('') # so '/' insde commands works correctly
    opt = input(">> ")
    return opt
