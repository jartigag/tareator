import os
import csv
import string
from datetime import datetime, timedelta

def register2echo(project, note, start_time, end_time):
    s, e = ( datetime.strftime(x, '%H:%M') if x.date()==datetime.today().date() else x.isoformat() for x in [start_time, end_time] )  # if today, just time. else, isoformat
    return f'''echo "{note} from {s} to {e}{ ' #'+project if project else '' }"'''

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
    '''returns first alias found in text (alias defined as a word starting with "#")'''
    aliases = [
        ''.join(c for c in word if c not in string.punctuation.replace("-",""))
    # ^^ filter every punctuation symbol except "-" (an alias may contain it) ^^
         for word in text.split() if word.startswith("#")
    ]
    if len(aliases)>0:
        return aliases[0]
    else:
        return False

def get_interval_hours():
    intervals = []
    try:
        with open("intervals.template") as intf:
            for line in intf.read().splitlines():
                if line and not line.startswith('#'):
                    intervals.append( [ datetime.strptime(h, '%H:%M').time() for h in line.split('-') ] ) # like "09:00-13:30" -> [09:00, 13:30]
    except:
        # interval by default:
        intervals = [ [ datetime.strptime('09:00', '%H:%M').time(), datetime.strptime('17:00', '%H:%M').time() ] ]
        #TODO: from "--open tareator--" to "--close tareator--"? from "--open tareator--" to "--commited until here--"?
    return intervals

def round_time(t):
    '''returns time rounding to the nearest 15 minute mark'''
    discarded_difference = timedelta(minutes=t.minute%15, seconds=t.second)
    rounded_t = t+timedelta(minutes=15)-discarded_difference if discarded_difference >= timedelta(minutes=15/2) else t-discarded_difference
    return rounded_t

def dump_commit(actions, publisher_function):
    intervals = get_interval_hours()
    days = sorted(set( a[0].date() for a in actions ))

    with open("commit.tmp","w") as cf:

        for actual_day in days:

            # set interval hours on actual day:
            actual_day_intervals = [ [ datetime.combine(actual_day, interval_hours) for interval_hours in interval ] for interval in intervals ]

            actual_day_actions = [ action for action in actions if action[0].date()==actual_day ]

            n = 0 # initial interval
            start_time = round_time(actual_day_intervals[n][0])

            for i,action in enumerate(reversed(actual_day_actions)):
            #                           ^^^ actions have been added from newest to oldest,
            #                               so now will be dumped to 'commit.tmp' in chronological order (from oldest to newest)

                end_time = round_time(actual_day_intervals[n][1])

                if action[0] < end_time:
                    end_time = round_time(action[0]) if i<len(actual_day_actions)-1 else round_time(actual_day_intervals[n][1])
                    note = action[1]
                    project = alias_from_text(note)
                    cf.write(f"{ globals()[publisher_function]( project, note, start_time, end_time ) }\n") # by default, globals()['register2shptime']
                    # set next start_time:
                    start_time = end_time
                else:
                    note = action[1]
                    project = alias_from_text(note)
                    cf.write(f"{ globals()[publisher_function]( project, note, start_time, end_time ) }\n") # by default, globals()['register2shptime']
                    # set next interval:
                    if n<len(actual_day_intervals)-1:
                        n+=1
                    else:
                        break

def edit_commit(dtime, register_file, publisher_function):
    actions = []
    def commit():
        dump_commit(actions, publisher_function)
        os.system( "editor commit.tmp" )
        push_commit()
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([dtime.isoformat(), "--committed until here--"])
    with open(register_file,"r+", newline='') as f:
        reader = csv.reader(f)
        lines = list( reader )
        for i,line in enumerate(reversed(lines)): # reading from most recent lines
            if not line[1]=="--committed until here--": # 1. get actions until "--committed--" line found:
                if not line[1]=="--open tareator--" and not line[1]=="--close tareator--":
                    actions.append([ datetime.strptime(line[0], '%Y-%m-%dT%H:%M:%S'), line[1].replace('"', "'") ]) # like [2020-02-02T10:00:00, 'report made']
                if i==len(lines)-1:
                    commit()
            else:
                if len(actions)>0:                      # 2. dump actions on 'commit.tmp', edit it and push it:
                    commit()
                else:
                    print("[-] nada para hacer commit")
                break

def prompt_commands(commands_list):
    try:
        from prompt_toolkit.completion import FuzzyWordCompleter
        from prompt_toolkit.shortcuts import prompt
        raise ImportError
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
    readline.set_completer_delims('') # so '/' inside commands works correctly
    opt = input(">> ")
    return opt
