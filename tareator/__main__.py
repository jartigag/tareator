#!/usr/bin/env python3

__version__ = "1.1"
__author__ = "@jartigag"
__url__ = "https://github.com/jartigag/tareator"

import sys
import csv
from os import system, path
from datetime import datetime

from .commands import parse_commands, prompt_commands, complete_commands
from .tasks_utils import bold, red, green
from .tasks_utils import reload_screen, add_task, mark_as_done, mark_as_wip, add_tasks_title

tasks_file = sys.argv[1] if len(sys.argv)>1 else 'README.md'
register_file = path.join( path.dirname(tasks_file), 'register{}.csv'.format( '' if len(sys.argv)==1 else '.'+path.splitext(path.basename(tasks_file))[0]) )

publisher_function = 'register2shptime'

def init(silent_flag=False):
    open(tasks_file,'a+').close() # touch
    open(register_file,'a+').close() # touch

    if len(sys.argv)>2:
        if sys.argv[2] in ("-s","--silent"):
            silent_flag = True

    now = datetime.now().replace(microsecond=0)
    if not silent_flag:
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
    marks = {
        'done': symbol,
        'wip': symbol.replace('x','/'),
        'to-do': symbol.replace('x',' ')
    }

    return marks, silent_flag

commands_list = ["/registro", "/commit", "/intervalos", "/clear", "/deshacer"]

basic_list_commands = f"""
{bold('lo que acabo de hacer')}       añade "lo que acabo de hacer" al registro de acciones

{bold('*una tarea pendiente')}        añade "una tarea pendiente" a la lista de tareas
{bold('1')}                           marca la tarea pendiente 1 como hecha
{bold('.5')}                          marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)"""

timetracker_commands = f"""
{bold('/registro')}                   imprime las acciones registradas desde el último commit
{bold('/commit')}                     revisa y publica las últimas tareas con {publisher_function}
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
tareator v{__version__}, de {__author__} ({__url__})
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

def write_register_file(action, dtime):
    with open(register_file,"a",newline='') as f: # if newline='' is not specified, newlines embedded inside quoted fields will not be interpreted correctly [..]
                                                  # https://docs.python.org/3/library/csv.html#id3
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([dtime.isoformat(), action])

def confirm_action(action, dtime):
    confirmation = input(f"registrar acción '{action}'? [S/n]").lower()
    if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
        reload_screen(tasks_file, marks)
        print(f"{green('[+]')} has registrado '{action}' a las { dtime.time().isoformat() }")
        return f"[+] {action}"
    else:
        print(f"{red('[-]')} no añadido")
        return False

def parse_chars(opt, marks, tasks, subtasks_titles, tasks_file):
    action = False
    if opt[0]=="*":
        add_task( opt[1:].strip(), tasks_file, tasks, marks )
    elif opt[0]==".":
        if opt[1:].isdigit():
            if int(opt[1:])<len(tasks):
                action = mark_as_wip( int(opt[1:]), now, tasks_file, tasks, marks )
            else:
                print(f"{red('[!]')} número inválido")
        else:
            print(f"{red('[!]')} número inválido")
    elif opt[0]=="#":
        if opt[1]=="*":
            add_task( opt[2:].strip(), tasks_file, tasks, marks, subtasks_titles[-1] )
        elif "*" in opt[1:]:
            if opt[1:opt.index("*")].isdigit():
                if int(opt[1:opt.index("*")])<len(subtasks_titles):
                    add_task( opt[3:].strip(), tasks_file, tasks, marks, subtasks_titles[ int(opt[1:opt.index("*")]) ] )
                else:
                    print(f"{red('[!]')} número inválido")
            else:
                print(f"{red('[!]')} número inválido")
        else:
            add_tasks_title( opt[1:].strip(), tasks_file, marks )
    else:
        action = confirm_action( opt, now )
    return action

if __name__ == '__main__':
    marks, silent_flag = init()
    tasks, subtasks_titles = reload_screen(tasks_file, marks)
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
                tasks, subtasks_titles = reload_screen(tasks_file, marks)
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> h")
                print(help_msg)
            elif opt=="hh":
                tasks, subtasks_titles = reload_screen(tasks_file, marks)
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> hh")
                print(hhelp_msg)
            elif opt=="e":
                system(f"editor {tasks_file}")
            elif opt=="r":
                system(f"editor {register_file}")
            elif opt.isdigit():
                if int(opt)<len(tasks):
                    action = mark_as_done( int(opt), now, tasks_file, tasks, marks )
                else:
                    print(f"{red('[!]')} número inválido")
            elif opt in commands_list:
                parse_commands(opt, now, marks, tasks, tasks_file, register_file, publisher_function)
            elif len(opt)>1:
                action = parse_chars(opt, marks, tasks, subtasks_titles, tasks_file)
            else:
                tasks, subtasks_titles = reload_screen(tasks_file, marks)

            if action:
                write_register_file( action, now )

        except EOFError:
            now = datetime.now().replace(microsecond=0)
            if not silent_flag:
                write_register_file('--close tareator--', now)
            print()
            sys.exit()
        except KeyboardInterrupt:
            now = datetime.now().replace(microsecond=0)
            if not silent_flag:
                write_register_file('--close tareator--', now)
            print()
            sys.exit()
