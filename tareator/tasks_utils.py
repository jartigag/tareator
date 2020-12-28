from os import system, path

def bold(text): return f"\033[1m{text}\033[0m"
def red(text): return f"\033[1;31m{text}\033[0m"
def green(text): return f"\033[1;32m{text}\033[0m"

basic_list_commands = f"""
{bold('lo que acabo de hacer')}       añade "lo que acabo de hacer" al registro de acciones

{bold('*una tarea pendiente')}        añade "una tarea pendiente" a la lista de tareas
{bold('1')}                           marca la tarea pendiente 1 como hecha
{bold('.5')}                          marca la tarea 5 como en progreso (si había otra en progreso, esa vuelve a pendiente)"""

advanced_list_commands = f"""
{bold('#un conjunto de subtareas')}   añade "un conjunto de subtareas" como título para varias subtareas
{bold('#*una subtarea pendiente')}    añade "una subtarea pendiente" como subtarea del último conjunto
{bold('#5*nueva subtarea')}           añade "nueva subtarea" al conjunto de subtareas 5"""

class Tasks:
    def __init__(self, tasks_file, marks):
        self.tasks_file = tasks_file
        self.marks = marks
        self.tasks = []
        self.subtasks_titles = []
        self.read_tasks_file()

    def read_tasks_file(self):
        system('clear')
        system('clear')
        self.tasks.clear()
        self.subtasks_titles.clear()
        last_title = ''
        print()
        print(f"{bold('[[ TAREATOR: lista {} ]]')}\n".format(path.basename(self.tasks_file)))
        with open(self.tasks_file) as f:
            for line in f.read().splitlines(): # ("\n" removed)
                status = "Error"
                splitted_line = line.split()
                if len(splitted_line)>1:
                    if splitted_line[0].strip()=="##":
                        last_title = " ".join(splitted_line[1:])
                        self.subtasks_titles.append(last_title)
                for k,v in self.marks.items():
                    n = len(v)
                    task = line.strip()[n:].strip()
                    first_chars = line.strip()[:n]
                    if first_chars==v:
                        status = k
                if status is not "Error":
                    self.tasks.append( {'task': task, 'status': status, 'title': last_title } )
        for t in self.tasks:
            if not t['title']:
                print(f"{self.tasks.index(t)}.{self.marks[t['status']]} {t['task']}")
        if self.subtasks_titles:
            for title in self.subtasks_titles:
                print(f"\n#{self.subtasks_titles.index(title)} {title}")
                for t in self.tasks:
                    if t['title']==title:
                        print(f"{self.tasks.index(t)}.{self.marks[t['status']]} {t['task']}")
        print()

    def write_tasks_file(self, new_task = {'task': '', 'status': '', 'title': ''}):
        with open(self.tasks_file) as inf, open("{}.tmp".format(self.tasks_file),"w") as outf:

            # split tasks in subtasks and not-subtasks (normal tasks):
            normal_tasks = [x for x in self.tasks if not x['title']]
            subtasks = [x for x in self.tasks if x['title']]

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
                                outf.write(f"{self.marks['to-do']} {new_task['task']}\n\n")
                            outf.write(line)

                    for i_t,t in enumerate(normal_tasks):
                        n = len(self.marks[t['status']])
                        task = line.strip()[n:].strip()
                        first_chars = line.strip()[:n]
                        if t['task']==task:
                        # update the new status of the present task
                            outf.write(line.replace( first_chars, self.marks[t['status']]) )
                            break
                        elif i_t==len(normal_tasks)-1:
                            outf.write(line)

                    # if this is the last line of the file and we're reading normal tasks yet,
                    # write the new task now:
                    if i_line==len(lines)-1:
                        if new_task['task']!='' and new_task['title']=='': outf.write(f"{self.marks['to-do']} {new_task['task']}\n")

                if writing_subtasks and (subtasks or new_task['title']!=''):
                # then the subtasks sections come:

                    if len(splitted_line)>1:
                        if splitted_line[0].strip()=="##":
                            if in_the_title:
                            # 2. we're about to enter on a different subtasks section,
                            # so write the new subtask at the bottom of this subtasks section
                                if new_task['task']!='': outf.write(f"{self.marks['to-do']} {new_task['task']}\n")
                                in_the_title = False
                            if new_task['task']!='' and new_task['title']==" ".join(splitted_line[1:]):
                            # 1. we're on the right subtasks section, so activate the flag..
                                in_the_title = True

                    for i_t,t in enumerate(subtasks):
                        n = len(self.marks[t['status']])
                        task = line.strip()[n:].strip()
                        first_chars = line.strip()[:n]
                        if t['task']==task:
                        # update the new status of the present task
                            outf.write(line.replace( first_chars, self.marks[t['status']]) )
                            break
                        elif i_t==len(subtasks)-1:
                            outf.write(line)

                    # if this is the last line of the file and we're reading the right subtasks section yet,
                    # write the new subtask now:
                    if in_the_title and i_line==len(lines)-1:
                        if new_task['task']!='': outf.write(f"{self.marks['to-do']} {new_task['task']}\n")

        # cosmetic adjustments:
        first_mark_chars = self.marks["done"][:-2].replace("[","\\[") # `- \[` or ` \[`, escaped to replace on perl
        system(f'perl -0pe "s/\\n\\n{first_mark_chars}/\\n{first_mark_chars}/g" -i {self.tasks_file}.tmp') # avoid double newlines
        system(f'perl -0pe "s/\\n\\n## /\\n## /g" -i {self.tasks_file}.tmp') # remove empty lines before titles
        system(f'perl -0pe "s/## /\\n## /g" -i {self.tasks_file}.tmp') # add one line before titles
        system(f'perl -0pe "s/^(##).*\\n\\n//gm" -i {self.tasks_file}.tmp') # remove titles without subtasks

        system(f'cat {self.tasks_file}.tmp > {self.tasks_file} && rm {self.tasks_file}.tmp') # to keep same inode (symbolic links)

    def add_task(self, task, subtask_title=''):
        new_task = {'task': task, 'status': "to-do", 'title': subtask_title }
        self.write_tasks_file(new_task)
        self.read_tasks_file()

    def mark_as_done(self, i, dtime):
        if self.tasks[i]['status'] is not "done":
            self.tasks[i]['status'] = "done"
            self.write_tasks_file()
            self.read_tasks_file()
            print(f"{green('[x]')} has marcado '{self.tasks[i]['task'].strip()}' como hecha a las { dtime.time().isoformat() }")
            return f"[x] {self.tasks[i]['task'].strip()}"
        else:
            print(f"{red('[!]')} '{self.tasks[i]['task'].strip()}' ya está marcada como hecha")
            return False

    def mark_as_wip(self, i, dtime):
        if self.tasks[i]['status']=="to-do":
            for j,t in enumerate(self.tasks):
                if self.tasks[j]['status']=="wip":
                    self.tasks[j]['status'] = "to-do" # only one "wip" task at a time
            self.tasks[i]['status'] = "wip"
            self.write_tasks_file()
            self.read_tasks_file()
            print(f"{green('[/]')} has marcado '{self.tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
            return f"[/] {self.tasks[i]['task'].strip()}"
        elif self.tasks[i]['status']=="wip":
            print(f"[!] aunque '{self.tasks[i]['task'].strip()}' ya estaba marcada como en progreso, se registrará esta acción con la hora actual")
            print(f"{green('[/]')} has marcado '{self.tasks[i]['task'].strip()}' como en progreso a las { dtime.time().isoformat() }")
            return f"[/] {self.tasks[i]['task'].strip()}"
        elif self.tasks[i]['status']=="done":
            print(f"{red('[!]')} '{self.tasks[i]['task'].strip()}' ya está marcada como hecha")
            return False

    def add_tasks_title(self, title):
        with open(self.tasks_file, 'a') as f:
            f.write(f"\n## {title}\n")
        self.read_tasks_file()
