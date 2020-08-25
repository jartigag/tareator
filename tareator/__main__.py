#!/usr/bin/env python3
#author: @jartigag
#date: 25/08/2020
#version: 0.9

import sys
from os import system, path
import csv
from datetime import datetime
from .timetracker import edit_commit, prompt_commands, complete_commands

tasks_file = 'README.md' if len(sys.argv)==1 else sys.argv[1]
tasks_file_basename = path.basename(tasks_file)

register_file = 'register{}.csv'.format( '' if len(sys.argv)==1 else '.'+path.splitext(tasks_file_basename)[0])

open(register_file,'a+').close() # touch

# support both styles on a tasks-list:
symbol = '[x]'
alt_symbol = '- [x]'

with open(tasks_file) as f:
    if any( alt_symbol.replace('x',c) in f.read() for c in 'x/ '):
    #                                         [x], [/], [ ] ^^^
        symbol = alt_symbol

mark = {
    'done': symbol,
    'wip': symbol.replace('x','/'),
    'to-do': symbol.replace('x',' ')
}

commands_list = ["/registro", "/commit", "/intervalos", "/clear", "/deshacer"]

def bold(text): return f"\033[1m{text}\033[0m"
def red(text): return f"\033[1;31m{text}\033[0m"
def green(text): return f"\033[1;32m{text}\033[0m"

help_msg = f"""la herramienta "tareator" responde interactivamente a lo que escribas. por ejemplo:

{bold('lo que acabo de hacer')}       añade "lo que acabo de hacer" al registro de acciones

{bold('*una tarea pendiente')}        añade "una tarea pendiente" a la lista de tareas
{bold('1')}                           marca la tarea pendiente 1 como hecha
{bold('.5')}                          marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)

{bold('/registro')}                   imprime las acciones registradas desde el último commit
{bold('/commit')}                     revisa y publica las últimas tareas con shptime
{bold('/intervalos')}                 edita los intervalos por defecto de tu jornada laboral
{bold('/clear')}                      elimina de la lista las tareas completadas
{bold('/deshacer')}                   elimina la última acción del registro de acciones

escribe 'hh' para mostrar la ayuda más detallada.
"""

hhelp_msg = f"""tareator v0.9, de @jartigag (https://github.com/jartigag/tareator)

...

tengo que escribir la ayuda detallada
* shptime
* describir el proceso de /commit:
  vuelca lo que hay en register.csv en tareas de shptime teniendo en cuenta intervals.template
* explicar alias
* explicar subtareas

== COMANDOS BÁSICOS DE LISTAS:
{bold('lo que acabo de hacer')}       añade "lo que acabo de hacer" al registro de acciones

{bold('*una tarea pendiente')}        añade "una tarea pendiente" a la lista de tareas
{bold('1')}                           marca la tarea pendiente 1 como hecha
{bold('.5')}                          marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)

== COMANDOS DE TIMETRACKER:
{bold('/registro')}                   imprime las acciones registradas desde el último commit
{bold('/commit')}                     revisa y publica las últimas tareas con shptime
{bold('/intervalos')}                 edita los intervalos por defecto de tu jornada laboral
{bold('/clear')}                      elimina de la lista las tareas completadas
{bold('/deshacer')}                   elimina la última acción del registro de acciones

== COMANDOS AVANZADOS DE LISTAS (más en la ayuda detallada):
{bold('#un conjunto de subtareas')}   añade "un conjunto de subtareas" como título para varias subtareas
{bold('#*una subtarea pendiente')}    añade "una subtarea pendiente" como subtarea del último conjunto
{bold('#5*nueva subtarea')}           añade "nueva subtarea" al conjunto de subtareas 5
"""

tasks = []
subtasks_titles = []

def reload_screen():
    system('clear')
    system('clear')
    read_tasks_file()

def read_tasks_file():
    tasks.clear()
    subtasks_titles.clear()
    last_title = ''
    print()
    print(f"{bold('[[ TAREATOR: lista {} ]]')}\n".format(tasks_file_basename))
    with open(tasks_file) as f:
        for line in f.read().splitlines(): # ("\n" removed)
            status = "Error"
            splitted_line = line.split()
            if len(splitted_line)>1:
                if splitted_line[0].strip()=="##":
                    last_title = " ".join(splitted_line[1:])
                    subtasks_titles.append(last_title)
            for k,v in mark.items():
                n = len(v)
                task = line.strip()[n:].strip()
                first_chars = line.strip()[:n]
                if first_chars==v:
                    status = k
            if status is not "Error":
                tasks.append( {'task': task, 'status': status, 'title': last_title } )
    for t in tasks:
        if not t['title']:
            print(f"{tasks.index(t)}.{mark[t['status']]} {t['task']}")
    if subtasks_titles:
        for title in subtasks_titles:
            print(f"\n#{subtasks_titles.index(title)} {title}")
            for t in tasks:
                if t['title']==title:
                    print(f"{tasks.index(t)}.{mark[t['status']]} {t['task']}")
    print()

def write_tasks_file(new_task = {'task': '', 'status': '', 'title': ''}):
    #TODO: rewrite/split/factorize this function

    with open(tasks_file) as inf, open("{}.tmp".format(tasks_file),"w") as outf:
        normal_tasks = [x for x in tasks if not x['title']]
        subtasks = [x for x in tasks if x['title']]
        lines = inf.readlines()
        writing_subtasks = False
        in_the_title = False
        for i_line,line in enumerate(lines):
            splitted_line = line.split()
            if not writing_subtasks:
                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                        writing_subtasks = True
                        if new_task['task']!='' and new_task['title']=='':
                            outf.write(f"{mark['to-do']} {new_task['task']}\n\n")
                        outf.write(line)
                        continue
                for i_t,t in enumerate(normal_tasks):
                    n = len(mark[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                        outf.write(line.replace( first_chars, mark[t['status']]) )
                        break
                    elif i_t==len(normal_tasks)-1:
                        outf.write(line)
            if subtasks and writing_subtasks:
                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                        if in_the_title:
                            outf.write(f"{mark['to-do']} {new_task['task']}\n\n")
                            in_the_title = False
                        if new_task['task']!='' and new_task['title']==" ".join(splitted_line[1:]):
                            in_the_title = True
                for i_t,t in enumerate(subtasks):
                    n = len(mark[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                        outf.write(line.replace( first_chars, mark[t['status']]) )
                        break
                    elif i_t==len(subtasks)-1:
                        outf.write(line)
                if in_the_title and i_line==len(lines)-1:
                    outf.write(f"{mark['to-do']} {new_task['task']}\n")
    system("mv {}.tmp {}".format(tasks_file, tasks_file))

def write_register_file(action, dtime):
    with open(register_file,"a",newline='') as f: # if newline='' is not specified, newlines embedded inside quoted fields will not be interpreted correctly [..]
                                                  # https://docs.python.org/3/library/csv.html#id3
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([dtime.isoformat(), action])

def add_task(task, subtask_title=''):
    new_task = {'task': task, 'status': "to-do", 'title': subtask_title }
    write_tasks_file(new_task)
    reload_screen()

def mark_as_done(i, dtime):
    if tasks[i]['status'] is not "done":
        tasks[i]['status'] = "done"
        write_tasks_file()
        reload_screen()
        print(f"{green('[x]')} has marcado '{tasks[i]['task'].strip()}' como hecha a las { dtime.time().isoformat() }")
        return f"[x] {tasks[i]['task'].strip()}"
    else:
        print(f"{red('[!]')} '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def mark_as_wip(i, dtime):
    if tasks[i]['status']=="to-do":
        for j,t in enumerate(tasks):
            if tasks[j]['status']=="wip":
                tasks[j]['status'] = "to-do" # only one "wip" task at a time
        tasks[i]['status'] = "wip"
        write_tasks_file()
        reload_screen()
        print(f"{green('[/]')} has marcado '{tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
        return f"[/] {tasks[i]['task'].strip()}"
    elif tasks[i]['status']=="wip":
        print(f"[!] aunque '{tasks[i]['task'].strip()}' ya estaba marcada como en progreso, se registrará esta acción con la hora actual")
        print(f"{green('[/]')} has marcado '{tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
        return f"[/] {tasks[i]['task'].strip()}"
    elif tasks[i]['status']=="done":
        print(f"{red('[!]')} '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def confirm_action(action, dtime):
    confirmation = input(f"registrar acción '{action}'? [S/n]").lower()
    if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
        reload_screen()
        print(f"{green('[+]')} has registrado '{action}' a las { dtime.time().isoformat() }")
        return f"[+] {action}"
    else:
        print(f"{red('[-]')} no añadido")
        return False

def clear_dones():
    with open(tasks_file) as readf, open(f"{tasks_file}.tmp","w") as writef:
        for line in readf.readlines():
            if not line.startswith(mark['done']):
                writef.write(line)
        system(f"mv {tasks_file}.tmp {tasks_file}")
    reload_screen()
    print(f"{green('[+]')} has limpiado las tareas completadas")

def print_register(register_file):
    printable = []
    with open(register_file, newline='') as f:
        reader = csv.reader(f)
        lines = list( reader )
        for line in reversed( lines ): # reading from most recent lines
            if not line[1]=="--committed until here--": # read until "--commited--" line found:
                printable.append(f"{line[0]},{line[1]}")
            else:
                break
    for p in reversed(printable): # printing in chronological order (from oldest to newest)
        print(p)

def undo(register_file):
    with open(register_file) as f:
        lines = f.readlines()
        last_line = lines[-1]
        confirmation = input(f"última acción:\n{last_line}eliminar esta acción? [S/n]").lower()
        if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
            lines = lines[:-1]
            with open(register_file,"w") as f:
                f.write("".join(lines))
            print(f"{green('[+]')} has eliminado la última acción")
        else:
            print(f"{red('[-]')} no eliminada")

def add_tasks_title(title):
    with open(tasks_file, 'a') as f:
        f.write(f"\n## {title}\n")
    reload_screen()

def parse_commands(opt):
    if opt=="/commit":
        edit_commit( now, register_file )
    elif opt=="/intervalos":
        system( "editor intervals.template" ) #tip: editor can be set with `$ sudo update-alternatives --config editor` or `export EDITOR="vim"` in .bashrc
    elif opt=="/registro":
        print_register( register_file )
    elif opt=="/clear":
        clear_dones()
    elif opt=="/deshacer":
        undo( register_file )

if __name__ == '__main__':
    reload_screen()
    while True:
        print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
        try:
            action = False
            try:
                opt = prompt_commands(commands_list)
            except ImportError:
                opt = complete_commands(commands_list)
            now = datetime.now().replace(microsecond=0)
            if opt=="h":
                print(help_msg)
            elif opt=="hh":
                print(hhelp_msg)
            elif opt.isdigit():
                if int(opt)<len(tasks):
                    action = mark_as_done( int(opt), now )
                else:
                    print(f"{red('[!]')} número inválido")
            elif opt in commands_list:
                parse_commands(opt)
            elif len(opt)>1:
                if opt[0]=="*":
                    add_task( opt[1:].strip() )
                elif opt[0]==".":
                    if opt[1:].isdigit():
                        if int(opt[1:])<len(tasks):
                            action = mark_as_wip( int(opt[1:]), now )
                        else:
                            print(f"{red('[!]')} número inválido")
                    else:
                        print(f"{red('[!]')} número inválido")
                elif opt[0]=="#":
                    if opt[1]=="*":
                        add_task( opt[2:].strip(), subtasks_titles[-1] )
                    elif "*" in opt[1:]:
                        if opt[1:opt.index("*")].isdigit():
                            if int(opt[1:opt.index("*")])<len(subtasks_titles):
                                add_task( opt[3:].strip(), subtasks_titles[ int(opt[1:opt.index("*")]) ] )
                            else:
                                print(f"{red('[!]')} número inválido")
                        else:
                            print(f"{red('[!]')} número inválido")
                    else:
                        add_tasks_title( opt[1:].strip() )
                else:
                    action = confirm_action( opt, now )
            else:
                reload_screen()
            if action:
                write_register_file( action, now )
        except EOFError:
            print()
            sys.exit()
        except KeyboardInterrupt:
            print()
            sys.exit()
