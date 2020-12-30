import csv
from os import system
from .timetracker import edit_commit
from .tasks_utils import bold, red, green

commands_list = ["/registro", "/commit", "/intervalos", "/clear", "/deshacer"]

publisher_function = 'register2shptime'

timetracker_commands = f"""
{bold('/registro')}                   imprime las acciones registradas desde el último commit
{bold('/commit')}                     revisa y publica las últimas tareas con {publisher_function}
{bold('/intervalos')}                 edita los intervalos por defecto de tu jornada laboral
{bold('/clear')}                      elimina de la lista las tareas completadas
{bold('/deshacer')}                   elimina la última acción del registro de acciones"""

def parse_commands(opt, now, t, register_file):
    if opt=="/commit":
        edit_commit( now, register_file, publisher_function )
    elif opt=="/intervalos":
        system( "editor intervals.template" ) #tip: editor can be set with `$ sudo update-alternatives --config editor` or `export EDITOR="vim"` in .bashrc
    elif opt=="/registro":
        print_register( register_file )
    elif opt=="/clear":
        clear_dones(t)
    elif opt=="/deshacer":
        undo( register_file )

def print_register(register_file):
    printable = []
    with open(register_file, newline='') as f:
        reader = csv.reader(f)
        lines = list( reader )
        for line in reversed( lines ): # reading from most recent lines
            if not line[1]=="--committed until here--": # read until "--committed--" line found:
                if not line[1]=="--open tareator--" and not line[1]=="--close tareator--":
                    printable.append(f"{line[0]},{line[1]}")
            else:
                break
    for p in reversed(printable): # printing in chronological order (from oldest to newest)
        print(p)

def clear_dones(t):
    with open(t.tasks_file) as readf, open(f"{t.tasks_file}.tmp","w") as writef:
        for line in readf.readlines():
            if not line.startswith(t.marks['done']):
                writef.write(line)
    system(f'cat {t.tasks_file}.tmp > {t.tasks_file} && rm {t.tasks_file}.tmp') # to keep same inode (symbolic links)
    t.write_tasks_file() # to clear empty titles
    t.read_tasks_file()
    print(f"{green('[+]')} has limpiado las tareas completadas")

def undo(register_file):
    with open(register_file) as f:
        lines = f.readlines()
        undoable_lines = lines
        while lines[-1].split(',')[1]=="--open tareator--" or lines[-1].split(',')[1]=="--close tareator--":
            undoable_lines = undoable_lines[:-1]
        confirmation = input(f"última acción:\n{undoable_lines[-1]}eliminar esta acción? [S/n]").lower()
        if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
            lines = lines[:-1]
            with open(register_file,"w") as f:
                f.write("".join(lines))
            print(f"{green('[+]')} has eliminado la última acción")
        else:
            print(f"{red('[-]')} no eliminada")

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
    def completer(text, i):
        command = [c for c in commands_list if c.startswith(text)]
        try:
            return command[i]
        except IndexError:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('') # so '/' inside commands works correctly
    opt = input(">> ")
    return opt
