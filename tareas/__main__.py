#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#TODO: clearer use of print() and print("\033[1m \033[0m")
#TODO: improve help_msg

import os, sys

tasks_file='README.md'
mark = { # define the marks you want, but
         # keep the same length on everyone
    'done': '- [x]',
    'wip': '- [/]',
    'to-do': '- [ ]'
}

help_msg = """\033[1mtareas\033[0m responde interactivamente a lo que escribas. por ejemplo:

\033[1m*una tarea pendiente\033[0m  añade "una tarea pendiente" a la lista de tareas

\033[1m1\033[0m                     marca la tarea pendiente 1 como hecha
\033[1m.1\033[0m                    marca la tarea 1 como en progreso

escribe 'hh' para mostrar la ayuda más detallada.
"""

hhelp_msg = """tareas v0.1, de @jartigag

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
            task = line.strip()[3:].strip()
            first_chars = line.strip()[:3]
            for i_t,t in enumerate(tasks):
                if t['task']==task:
                    outf.write(line.replace(first_chars, mark(t['status'])))
                    break
                elif i_t==len(tasks)-1:
                    outf.write(line)
    os.system("mv {}.tmp {}".format(tasks_file, tasks_file))

def add_task(task):
    tasks.append( {'task': task, 'status': "to-do" } )
    with open(tasks_file,"a") as f:
        f.write(f"[ ] {task}\n")
    reload_screen()

def mark_as_done(i):
    if tasks[i]['status'] is not "done":
        tasks[i]['status'] = "done"
        write_tasks_file()
        reload_screen()
        print(f"[x] has marcado '{tasks[i]['task'].strip()}' como hecha")
    else:
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como hecha")

def mark_as_wip(i):
    if tasks[i]['status']=="to-do":
        for t in tasks:
            if t['task']=="wip":
                t['task'] = "to-do" # only one "wip" task at a time
        tasks[i]['status'] = "wip"
        write_tasks_file()
        reload_screen()
        print(f"[/] has marcado '{tasks[i]['task'].strip()}' como \"en progreso\"")
    elif tasks[i]['status']=="wip":
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como \"en progreso\"")
    elif tasks[i]['status']=="done":
        print(f"[!] '{tasks[i]['task'].strip()}' ya está marcada como hecha")

if __name__ == '__main__':
    reload_screen()
    while True:
        print("\033[1m{}\033[0m {}".format("qué estás haciendo?","('h' para mostrar la ayuda, Intro para recargar)"))
        try:
            opt = input(">> ")
            if opt=="h":
                print(help_msg)
            elif opt=="hh":
                print(hhelp_msg)
            elif len(opt)>1:
                if opt[0]=="*":
                    add_task( opt[1:].strip() )
                elif opt[0]==".":
                    if opt[1:].isdigit():
                        if int(opt[1:])<len(tasks):
                            mark_as_wip( int(opt[1:]) )
                        else:
                            print("número inválido")
                    else:
                        print("número inválido")
                else:
                    reload_screen()
            elif opt.isdigit():
                if int(opt)<len(tasks):
                    mark_as_done( int(opt) )
                else:
                    print("número inválido")
            else:
                reload_screen()
        except EOFError:
            print()
            sys.exit()
        except KeyboardInterrupt:
            print()
            sys.exit()
