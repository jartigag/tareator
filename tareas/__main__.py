#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#TODO: clearer use of print() and print("\033[1m \033[0m")
#TODO: improve help_msg

import os, sys
from datetime import datetime

tasks_file='README.md'
logbook_file='logbook.csv'
mark = {
    'done': '- [x]',
    'wip': '- [/]',
    'to-do': '- [ ]'
}

help_msg = """\033[1mtareas\033[0m responde interactivamente a lo que escribas. por ejemplo:

\033[1m*una tarea pendiente\033[0m  añade "una tarea pendiente" a la lista de tareas

\033[1m1\033[0m                     marca la tarea pendiente 1 como hecha
\033[1m.5\033[0m                    marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)

\033[1mlo que acabo de hacer\033[0m añade "lo que acabo de hacer" al registro de acciones

escribe 'hh' para mostrar la ayuda más detallada.
"""

hhelp_msg = """tareas v0.2, de @jartigag

...

tengo que escribir la ayuda detallada
"""

tasks = []

def reload_screen():
    os.system('clear')
    os.system('clear')
    read_tasks_file()

def read_tasks_file():
    tasks.clear()
    print()
    print("\033[1m[[ lista de TAREAS ]]\033[0m\n")
    with open(tasks_file) as f:
        for line in f.read().splitlines(): # ("\n" removed)
            status = "Error"
            for k,v in mark.items():
                n = len(v)
                task = line.strip()[n:].strip()
                first_chars = line.strip()[:n]
                if first_chars==v:
                    status = k
            if status is not "Error":
                tasks.append( {'task': task, 'status': status } )
    for t in tasks:
        print(f"{tasks.index(t)}.{mark[t['status']]} {t['task']}")
    print()

def write_tasks_file():
    with open(tasks_file) as inf, open("{}.tmp".format(tasks_file),"w") as outf:
        lines = inf.readlines()
        for i_line,line in enumerate(lines):
            for i_t,t in enumerate(tasks):
                n = len(mark[t['status']])
                task = line.strip()[n:].strip()
                first_chars = line.strip()[:n]
                if t['task']==task:
                    outf.write(line.replace( first_chars, mark[t['status']]) )
                    break
                elif i_t==len(tasks)-1:
                    outf.write(line)
    os.system("mv {}.tmp {}".format(tasks_file, tasks_file))

def write_logbook_file(action,time):
    with open(logbook_file,"a") as f:
        f.write(f"{time},{action}\n")

def add_task(task):
    tasks.append( {'task': task, 'status': "to-do" } )
    with open(tasks_file,"a") as f:
        f.write(f"{mark['to-do']} {task}\n")
    reload_screen()
    return f"[ ] {task.strip()}"

def mark_as_done(i, time):
    if tasks[i]['status'] is not "done":
        tasks[i]['status'] = "done"
        write_tasks_file()
        reload_screen()
        print(f"[x] has marcado '{tasks[i]['task'].strip()}' como hecha a las {time}")
        return f"[x] {tasks[i]['task'].strip()}"
    else:
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def mark_as_wip(i, time):
    if tasks[i]['status']=="to-do":
        for j,t in enumerate(tasks):
            if tasks[j]['status']=="wip":
                tasks[j]['status'] = "to-do" # only one "wip" task at a time
        tasks[i]['status'] = "wip"
        write_tasks_file()
        reload_screen()
        print(f"[/] has marcado '{tasks[i]['task'].strip()}' como en progreso a las {time}")
        return f"[/] {tasks[i]['task'].strip()}"
    elif tasks[i]['status']=="wip":
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como en progreso")
        return False
    elif tasks[i]['status']=="done":
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def confirm_action(action, time):
    confirmation = input(f"registrar acción '{action}'? [S/n]").lower()
    if confirmation.startswith('s') or confirmation.startswith('y') or confirmation=="":
        reload_screen()
        print(f"[+] has registrado '{action}' a las {time}")
        return f"[+] {action}"
    else:
        print("[-] no añadido")
        return False

if __name__ == '__main__':
    reload_screen()
    while True:
        print("\033[1m{}\033[0m {}".format("qué estás haciendo?","('h' para mostrar la ayuda, Intro para recargar)"))
        try:
            action = False
            opt = input(">> ")
            now = datetime.now().replace(microsecond=0).isoformat()
            if opt=="h":
                print(help_msg)
            elif opt=="hh":
                print(hhelp_msg)
            elif opt.isdigit():
                if int(opt)<len(tasks):
                    action = mark_as_done( int(opt), now.split('T')[1] )
                    #                                 ^^^^^ example: 09:30:00
                else:
                    print("número inválido")
            elif len(opt)>1:
                if opt[0]=="*":
                    add_task( opt[1:].strip() )
                elif opt[0]==".":
                    if opt[1:].isdigit():
                        if int(opt[1:])<len(tasks):
                            action = mark_as_wip( int(opt[1:]), now.split('T')[1] )
                        else:
                            print("número inválido")
                    else:
                        print("número inválido")
                else:
                    action = confirm_action( opt, now.split('T')[1] )
            else:
                reload_screen()
            if action:
                write_logbook_file( action, now )
        except EOFError:
            print()
            sys.exit()
        except KeyboardInterrupt:
            print()
            sys.exit()
