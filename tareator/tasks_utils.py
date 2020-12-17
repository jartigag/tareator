from os import system, path

def bold(text): return f"\033[1m{text}\033[0m"
def red(text): return f"\033[1;31m{text}\033[0m"
def green(text): return f"\033[1;32m{text}\033[0m"

def reload_screen(tasks_file, marks, tasks=[], subtasks_titles=[]):
    system('clear')
    system('clear')
    tasks, subtasks_titles = read_tasks_file(tasks, subtasks_titles, marks, tasks_file)
    return tasks, subtasks_titles

def read_tasks_file(tasks, subtasks_titles, marks, tasks_file):
    tasks.clear()
    subtasks_titles.clear()
    last_title = ''
    print()
    print(f"{bold('[[ TAREATOR: lista {} ]]')}\n".format(path.basename(tasks_file)))
    with open(tasks_file) as f:
        for line in f.read().splitlines(): # ("\n" removed)
            status = "Error"
            splitted_line = line.split()
            if len(splitted_line)>1:
                if splitted_line[0].strip()=="##":
                    last_title = " ".join(splitted_line[1:])
                    subtasks_titles.append(last_title)
            for k,v in marks.items():
                n = len(v)
                task = line.strip()[n:].strip()
                first_chars = line.strip()[:n]
                if first_chars==v:
                    status = k
            if status is not "Error":
                tasks.append( {'task': task, 'status': status, 'title': last_title } )
    for t in tasks:
        if not t['title']:
            print(f"{tasks.index(t)}.{marks[t['status']]} {t['task']}")
    if subtasks_titles:
        for title in subtasks_titles:
            print(f"\n#{subtasks_titles.index(title)} {title}")
            for t in tasks:
                if t['title']==title:
                    print(f"{tasks.index(t)}.{marks[t['status']]} {t['task']}")
    print()
    return tasks, subtasks_titles

def write_tasks_file(tasks, marks, tasks_file, new_task = {'task': '', 'status': '', 'title': ''}):
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
                            outf.write(f"{marks['to-do']} {new_task['task']}\n\n")
                        outf.write(line)

                for i_t,t in enumerate(normal_tasks):
                    n = len(marks[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                    # update the new status of the present task
                        outf.write(line.replace( first_chars, marks[t['status']]) )
                        break
                    elif i_t==len(normal_tasks)-1:
                        outf.write(line)

                # if this is the last line of the file and we're reading normal tasks yet,
                # write the new task now:
                if i_line==len(lines)-1:
                    if new_task['task']!='' and new_task['title']=='': outf.write(f"{marks['to-do']} {new_task['task']}\n")

            if writing_subtasks and (subtasks or new_task['title']!=''):
            # then the subtasks sections come:

                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                        if in_the_title:
                        # we're about to enter on a different subtasks section,
                        # so write the new subtask at the bottom of this subtasks section
                            if new_task['task']!='': outf.write(f"{marks['to-do']} {new_task['task']}\n")
                            in_the_title = False
                        if new_task['task']!='' and new_task['title']==" ".join(splitted_line[1:]):
                        # we're on the right subtasks section, so activate the flag..
                            in_the_title = True

                for i_t,t in enumerate(subtasks):
                    n = len(marks[t['status']])
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if t['task']==task:
                    # update the new status of the present task
                        outf.write(line.replace( first_chars, marks[t['status']]) )
                        break
                    elif i_t==len(subtasks)-1:
                        outf.write(line)

                # if this is the last line of the file and we're reading the right subtasks section yet,
                # write the new subtask now:
                if in_the_title and i_line==len(lines)-1:
                    if new_task['task']!='': outf.write(f"{marks['to-do']} {new_task['task']}\n")

    # cosmetic adjustments:
    first_mark_chars = marks["done"][:-2].replace("[","\\[") # `- \[` or ` \[`, escaped to replace on perl
    system(f'perl -0pe "s/\\n\\n{first_mark_chars}/\\n{first_mark_chars}/g" -i {tasks_file}.tmp') # avoid double newlines
    system(f'perl -0pe "s/\\n\\n## /\\n## /g" -i {tasks_file}.tmp') # remove empty lines before titles
    system(f'perl -0pe "s/## /\\n## /g" -i {tasks_file}.tmp') # add one line before titles
    system(f'perl -0pe "s/^(##).*\\n\\n//gm" -i {tasks_file}.tmp') # remove titles without subtasks

    system(f'cat {tasks_file}.tmp > {tasks_file} && rm {tasks_file}.tmp') # to keep same inode (symbolic links)

def add_task(task, tasks_file, tasks, marks, subtask_title=''):
    new_task = {'task': task, 'status': "to-do", 'title': subtask_title }
    write_tasks_file(tasks, marks, tasks_file, new_task)
    reload_screen(tasks_file, marks)

def mark_as_done(i, dtime, tasks_file, tasks, marks):
    if tasks[i]['status'] is not "done":
        tasks[i]['status'] = "done"
        write_tasks_file(tasks, marks, tasks_file)
        reload_screen(tasks_file, marks)
        print(f"{green('[x]')} has marcado '{tasks[i]['task'].strip()}' como hecha a las { dtime.time().isoformat() }")
        return f"[x] {tasks[i]['task'].strip()}"
    else:
        print(f"{red('[!]')} '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def mark_as_wip(i, dtime, tasks_file, tasks, marks):
    if tasks[i]['status']=="to-do":
        for j,t in enumerate(tasks):
            if tasks[j]['status']=="wip":
                tasks[j]['status'] = "to-do" # only one "wip" task at a time
        tasks[i]['status'] = "wip"
        write_tasks_file(tasks, marks, tasks_file)
        reload_screen(tasks_file, marks)
        print(f"{green('[/]')} has marcado '{tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
        return f"[/] {tasks[i]['task'].strip()}"
    elif tasks[i]['status']=="wip":
        print(f"[!] aunque '{tasks[i]['task'].strip()}' ya estaba marcada como en progreso, se registrará esta acción con la hora actual")
        print(f"{green('[/]')} has marcado '{tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
        return f"[/] {tasks[i]['task'].strip()}"
    elif tasks[i]['status']=="done":
        print(f"{red('[!]')} '{tasks[i]['task'].strip()}' ya está marcada como hecha")
        return False

def add_tasks_title(title):
    with open(tasks_file, 'a') as f:
        f.write(f"\n## {title}\n")
    reload_screen(tasks_file, marks)
