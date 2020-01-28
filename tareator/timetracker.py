import os
import csv
import string
from datetime import datetime

def register2shptime(project, note, start_time, end_time):
    if not project:
        project = 'Otros' # project by default
    s, e = ( datetime.strftime(x, '%H:%M') if x.date()==datetime.today().date() else x.isoformat() for x in [start_time, end_time] )  # if today, just time. else, isoformat
    return f'shptime add -n {project} -t "{note}" -s {s} -e {e}'

def push_commit():
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

def dump_commit(actions):
    #TODO: improve this function
    with open("commit.tmp","w") as cf:
        starts = []
        ends = []
        with open("intervals.template") as intf:
            for line in intf.read().splitlines():
                if line and not line.startswith('#'):
                    s,e = line.split('-') # like "09:00-13:30"
                    starts.append( datetime.today().replace(hour=int(s.split(':')[0]), minute=int(s.split(':')[1]), second=0, microsecond=0) )
                    ends.append( datetime.today().replace(hour=int(e.split(':')[0]), minute=int(e.split(':')[1]), second=0, microsecond=0) )
        if not starts:
            starts.append( datetime.today().replace(hour=9, minute=0, second=0, microsecond=0) ) #starts[0]=09:00 by default
        i=0
        start_time = starts[0]
        for action in reversed(actions): # actions have been added from newest to oldest,
                                         # so now will be dumped to 'commit.tmp' in chronological order (from oldest to newest)
            note = action[1]
            project = alias_from_text(note)
            this_time = datetime.strptime(action[0], '%Y-%m-%dT%H:%M:%S')
            while starts[i]>this_time:
                i+=1 # find next applicable start_time
                start_time = starts[i]
            end_time = this_time
            cf.write(f"{ register2shptime( project, note, start_time, end_time ) }\n")
            while ends[i]<this_time:
                i+=1 # find next applicable end_time
                end_time = ends[i]
            start_time = end_time # so next action starts on the end_time of this action

def edit_commit(dtime, register_file):
    actions = []
    with open(register_file,"r+", newline='') as f:
        reader = csv.reader(f)
        lines = list( reader ) # ugh.. better way?
        for line in reversed( lines ): # reading from most recent lines
            if not line[1]=="--committed until here--": # 1. get actions until "--commited--" line found:
                actions.append([line[0],line[1].replace('"', "'")]) #TODO: cleaner way?
            else:
                if len(actions)>0:                   # 2. dump actions on 'commit.tmp', edit it and push it:
                    dump_commit(actions)
                    os.system( "editor commit.tmp" )
                    push_commit()
                    writer = csv.writer(f, newline='')
                    writer.writerow([dtime.isoformat(), "--committed until here--"])
                else:
                    print("[-] nada para hacer commit")
                break

def prompt_commands(commands_list):
    try:
        from prompt_toolkit.completion import FuzzyWordCompleter
        from prompt_toolkit.shortcuts import prompt
        commands = FuzzyWordCompleter(commands_list)
        opt = prompt(">> ", completer=commands, complete_while_typing=True)
        return opt
    except ImportError:
        raise ImportError

def complete_commands(commands_list):
    import readline
    commands = commands_list
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
