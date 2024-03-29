#!/usr/bin/env python3

__version__ = "1.3"
__author__ = "@jartigag"
__url__ = "https://github.com/jartigag/tareator"

import sys
import csv
from os import system, path
from datetime import datetime

#class:
from .tasks_utils import Tasks
#functions:
from .commands    import parse_commands, prompt_commands, complete_commands
from .tasks_utils import bold, red, green
#variables:
from .commands    import commands_list, timetracker_commands
from .tasks_utils import basic_taskscommands, advanced_taskscommands

tasks_file = sys.argv[1] if len(sys.argv)>1 else 'README.md'
register_file = path.join( path.dirname(tasks_file), 'register{}.csv'.format( '' if len(sys.argv)==1 else '.'+path.splitext(path.basename(tasks_file))[0]) )

def init(silent_flag=False, publisher_function='register2shptime'):
    open(tasks_file,'a+').close() # touch
    open(register_file,'a+').close() # touch

    if len(sys.argv)>2:
        if sys.argv[2] in ("-s","--silent"):
            silent_flag = True
        if sys.argv[2]=='register2echo':
            publisher_function = 'register2echo'
        if len(sys.argv)>3:
            if sys.argv[3] in ("-s","--silent"):
                silent_flag = True
            if sys.argv[3]=='register2echo':
                publisher_function = 'register2echo'

    now = datetime.now().replace(microsecond=0)
    if not silent_flag:
        write_register_file('--open tareator--', now)

    # support both styles on a tasks-list:
    symbol = '[x]'
    alt_symbol = '- [x]'
    with open(tasks_file) as f:
        fi = f.read()
        if any( alt_symbol.replace('x',c) in fi for c in 'x/ '):
        #                                   [x], [/], [ ] ^^^
            symbol = alt_symbol
    marks = {
        'done': symbol,
        'wip': symbol.replace('x','/'),
        'to-do': symbol.replace('x',' ')
    }

    return marks, silent_flag, publisher_function

def help_msg(publisher_function):
    print(f"""la herramienta "tareator" responde interactivamente a lo que escribas. por ejemplo:
{basic_taskscommands}
{timetracker_commands(publisher_function)}

escribe 'hh' para mostrar la ayuda más detallada.
""")

def hhelp_msg(publisher_function):
    print(f"""
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

== COMANDOS BÁSICOS DE TAREAS:{basic_taskscommands}

== COMANDOS DE TIMETRACKER:{timetracker_commands(publisher_function)}

== COMANDOS AVANZADOS DE TAREAS:{advanced_taskscommands}
""")

def write_register_file(action, dtime):
    with open(register_file,"a",newline='') as f: # if newline='' is not specified, newlines embedded inside quoted fields will not be interpreted correctly [..]
                                                  # https://docs.python.org/3/library/csv.html#id3
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([dtime.isoformat(), action])

def confirm_action(action, dtime):
    confirmation = input(f"registrar acción '{action}'? [S/n]").lower()
    if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
        t.read_tasks_file()
        print(f"{green('[+]')} has registrado '{action}' a las { dtime.time().isoformat() }")
        return f"[+] {action}"
    else:
        print(f"{red('[-]')} no añadido")
        return False

def parse_chars(opt, t):
    action = False
    if opt[0]=="*":
        t.add_task( opt[1:].strip())
    elif opt[0]==".":
        if opt[1:].isdigit():
            if int(opt[1:])<len(t.tasks):
                action = t.mark_as_wip( int(opt[1:]), now )
            else:
                print(f"{red('[!]')} número inválido")
        else:
            print(f"{red('[!]')} número inválido")
    elif opt[0]=="#":
        if opt[1]=="*":
            t.add_task( opt[2:].strip(), t.subtasks_titles[-1] )
        elif "*" in opt[1:]:
            if opt[1:opt.index("*")].isdigit():
                if int(opt[1:opt.index("*")])<len(t.subtasks_titles):
                    t.add_task( opt[3:].strip(), t.subtasks_titles[ int(opt[1:opt.index("*")]) ] )
                else:
                    print(f"{red('[!]')} número inválido")
            else:
                print(f"{red('[!]')} número inválido")
        else:
            t.add_tasks_title( opt[1:].strip() )
    else:
        action = confirm_action( opt, now )
    return action

if __name__ == '__main__':
    marks, silent_flag, publisher_function = init()
    t = Tasks(tasks_file, marks)
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
                t.read_tasks_file()
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> h")
                help_msg(publisher_function)
            elif opt=="hh":
                t.read_tasks_file()
                print(f"{bold('qué estás haciendo?')} ('h' para mostrar la ayuda, Intro para recargar)")
                print(">> hh")
                hhelp_msg(publisher_function)
            elif opt=="e":
                system(f"editor {tasks_file}")
            elif opt=="r":
                system(f"editor {register_file}")
            elif opt.isdigit():
                if int(opt)<len(t.tasks):
                    action = t.mark_as_done(int(opt), now)
                else:
                    print(f"{red('[!]')} número inválido")
            elif opt in commands_list:
                parse_commands(opt, now, t, register_file, publisher_function)
            elif len(opt)>1:
                action = parse_chars(opt, t)
            else:
                t.read_tasks_file()

            if action:
                write_register_file(action, now)

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
