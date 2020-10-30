#!/usr/bin/env python3
#author: @jartigag
#date: 10/09/2020
#version: 1.0

import sys
from os import system, path
import csv
from datetime import datetime
from .timetracker import edit_commit, prompt_commands, complete_commands

tasks_file = sys.argv[1] if len(sys.argv)>1 else 'README.md'
tasks_file_basename = path.basename(tasks_file)
register_file = path.dirname(tasks_file) + '/register{}.csv'.format( '' if len(sys.argv)==1 else '.'+path.splitext(tasks_file_basename)[0])
publisher_function = sys.argv[2] if len(sys.argv)>2 else 'register2shptime'

mark = {}

def init():
    global mark

    open(tasks_file,'a+').close() # touch
    open(register_file,'a+').close() # touch

    now = datetime.now().replace(microsecond=0)
    write_register_file('--open tareator--', now)

    # support both styles on a tasks-list:
    symbol = '[x]'
    alt_symbol = '- [x]'
    alt_symbol2 = '- [x]:'
    with open(tasks_file) as f:
        fi = f.read()
        if any( alt_symbol.replace('x',c) in fi for c in 'x/ '):
        #                                   [x], [/], [ ] ^^^
            symbol = alt_symbol
        if any( alt_symbol2.replace('x',c) in fi for c in 'x/ '):
        #                                    [x], [/], [ ] ^^^
            symbol = alt_symbol2
    mark = {
        'done': symbol,
        'wip': symbol.replace('x','/'),
        'to-do': symbol.replace('x',' ')
    }

commands_list = ["/registro", "/commit", "/intervalos", "/clear", "/deshacer"]

def bold(text): return f"\033[1m{text}\033[0m"
def red(text): return f"\033[1;31m{text}\033[0m"
def green(text): return f"\033[1;32m{text}\033[0m"

basic_list_commands = f"""
{bold('lo que acabo de hacer')}       añade "lo que acabo de hacer" al registro de acciones

{bold('*una tarea pendiente')}        añade "una tarea pendiente" a la lista de tareas
{bold('1')}                           marca la tarea pendiente 1 como hecha
{bold('.5')}                          marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)"""

timetracker_commands = f"""
{bold('/registro')}                   imprime las acciones registradas desde el último commit
{bold('/commit')}                     revisa y publica las últimas tareas con shptime
{bold('/intervalos')}                 edita los intervalos por defecto de tu jornada laboral
{bold('/clear')}                      elimina de la lista las tareas completadas
{bold('/deshacer')}                   elimina la última acción del registro de acciones"""

help_msg = f"""la herramienta "tareator" responde interactivamente a lo que escribas. por ejemplo:
{basic_list_commands}
{timetracker_commands}

escribe 'hh' para mostrar la ayuda más detallada.
"""

advanced_list_commands = f"""
{bold('#un conjunto de subtareas')}   añade "un conjunto de subtareas" como título para varias subtareas
{bold('#*una subtarea pendiente')}    añade "una subtarea pendiente" como subtarea del último conjunto
{bold('#5*nueva subtarea')}           añade "nueva subtarea" al conjunto de subtareas 5"""

hhelp_msg = f"""
tareator v1.0, de @jartigag (https://github.com/jartigag/tareator)
-----

escribí este script para solventar dos requerimientos comunes en una jornada laboral:
 - anotar las tareas pendientes
 - rellenar cómodamente el registro de horas con lo que he hecho

el funcionamiento de {bold('tareator')} se basa simplemente en dos ficheros de texto: una lista (que podría llamarse,
por ejemplo, tareas.md) y register.csv como histórico.

durante la jornada voy marcando tareas como en progreso o completadas, y apunto qué otras cosas he hecho.

cuando termino todo (o en cualquier momento de ese o de otro día), envío a la empresa el reporte de en qué
he estado trabajando. esto lo hago con el commando {bold('/commit')}, que vuelca lo que se ha escrito en register.csv
desde el último commit.

antes de enviar nada, se ajustan los intervalos de cada acción teniendo en cuenta los que hayas definido en
intervals.template (si no lo has hecho, la jornada por defecto va de 9.00 a 17.00), se redondean al cuarto
de hora y se abren en un editor de texto para poder modificarlos. cuando se cierra el editor, se ejecutan
las líneas de ese fichero.

en mi caso, uso por debajo una herramienta interna llamada {bold('shptime')} que publica en el timetracker de mi
empresa, pero puede sustituirse la función register2shptime() por el "publicador" que se quiera.

una funcionalidad muy interesante es etiquetar con {bold('alias de proyectos')} cada acción que se introduce.
si escribo "explicar cómo funciona #tareator", cuando haga /commit, el publicador (en este caso, shptime)
recibirá "tareator" como proyecto al que debe asignar esas horas.

además, también se pueden usar {bold('conjuntos de subtareas')} para agrupar tareas relacionadas bajo un mismo título.
esto puede ayudar a nivel organizativo, si quieres tener varias listas en un único fichero (por ejemplo,
tareas.md). por lo demás, funcionan igual.

== COMANDOS BÁSICOS DE LISTAS:{basic_list_commands}

== COMANDOS DE TIMETRACKER:{timetracker_commands}

== COMANDOS AVANZADOS DE LISTAS:{advanced_list_commands}
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
    with open(tasks_file) as inf, open("{}.tmp".format(tasks_file),"w") as outf:

        # split tasks in subtasks and not-subtasks (normal tasks):
        normal_tasks = [x for x in tasks if not x['title']]
        subtasks = [x for x in tasks if x['title']]

        lines = inf.readlines()
        if len(lines)==0: lines = [""] # for empty tasks_files

        writing_subtasks = False
        in_the_title = False

        for i_line,line in enumerate(lines):

            splitted_line = line.split()

            if not writing_subtasks:
            # normal tasks are on first place:

                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                    # now we're entering on the subtasks sections..
                        writing_subtasks = True
                        if new_task['task']!='' and new_task['title']=='':
                    # ..so if new task is a normal task, write it just before the subtasks sections
                            outf.write(f"{mark['to-do']} {new_task['task']}\n\n")
                        outf.write(line)

                for i_t,t in enumerate(normal_tasks):
                    n = len(mark[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                    # update the new status of the present task
                        outf.write(line.replace( first_chars, mark[t['status']]) )
                        break
                    elif i_t==len(normal_tasks)-1:
                        outf.write(line)

                # if this is the last line of the file and we're reading normal tasks yet,
                # write the new task now:
                if i_line==len(lines)-1:
                    if new_task['task']!='' and new_task['title']=='': outf.write(f"{mark['to-do']} {new_task['task']}\n")

            if writing_subtasks and (subtasks or new_task['title']!=''):
            # then the subtasks sections come:

                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                        if in_the_title:
                        # we're about to enter on a different subtasks section,
                        # so write the new subtask at the bottom of this subtasks section
                            if new_task['task']!='': outf.write(f"{mark['to-do']} {new_task['task']}\n")
                            in_the_title = False
                        if new_task['task']!='' and new_task['title']==" ".join(splitted_line[1:]):
                        # we're on the right subtasks section, so activate the flag..
                            in_the_title = True

                for i_t,t in enumerate(subtasks):
                    n = len(mark[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                    # update the new status of the present task
                        outf.write(line.replace( first_chars, mark[t['status']]) )
                        break
                    elif i_t==len(subtasks)-1:
                        outf.write(line)

                # if this is the last line of the file and we're reading the right subtasks section yet,
                # write the new subtask now:
                if in_the_title and i_line==len(lines)-1:
                    if new_task['task']!='': outf.write(f"{mark['to-do']} {new_task['task']}\n")

    # cosmetic adjustments:
    first_mark_chars = mark["done"][:-2].replace("[","\\[") # `- \[` or ` \[`, escaped to replace on perl
    system(f'perl -0pe "s/\\n\\n{first_mark_chars}/\\n{first_mark_chars}/g" -i {tasks_file}.tmp') # avoid double newlines
    system(f'perl -0pe "s/\\n\\n## /\\n## /g" -i {tasks_file}.tmp') # remove empty lines before titles
    system(f'perl -0pe "s/## /\\n## /g" -i {tasks_file}.tmp') # add one line before titles
    system(f'perl -0pe "s/^(##).*\\n\\n//gm" -i {tasks_file}.tmp') # remove titles without subtasks

    system(f'cat {tasks_file}.tmp > {tasks_file} && rm {tasks_file}.tmp') # to keep same inode (symbolic links)

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
    system(f'cat {tasks_file}.tmp > {tasks_file} && rm {tasks_file}.tmp') # to keep same inode (symbolic links)
    write_tasks_file() # to clear empty titles
    reload_screen()
    print(f"{green('[+]')} has limpiado las tareas completadas")

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

def add_tasks_title(title):
    with open(tasks_file, 'a') as f:
        f.write(f"\n## {title}\n")
    reload_screen()

def parse_commands(opt):
    if opt=="/commit":
        edit_commit( now, register_file, publisher_function )
    elif opt=="/intervalos":
        system( "editor intervals.template" ) #tip: editor can be set with `$ sudo update-alternatives --config editor` or `export EDITOR="vim"` in .bashrc
    elif opt=="/registro":
        print_register( register_file )
    elif opt=="/clear":
        clear_dones()
    elif opt=="/deshacer":
        undo( register_file )

if __name__ == '__main__':
    init()
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
                reload_screen()
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> h")
                print(help_msg)
            elif opt=="hh":
                reload_screen()
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> hh")
                print(hhelp_msg)
            elif opt=="e":
                system(f"editor {tasks_file}")
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
            now = datetime.now().replace(microsecond=0)
            write_register_file('--close tareator--', now)
            print()
            sys.exit()
        except KeyboardInterrupt:
            now = datetime.now().replace(microsecond=0)
            write_register_file('--close tareator--', now)
            print()
            sys.exit()
