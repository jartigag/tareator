#!/bin/bash
#author: @jartigag
#date: 09/11/2020

#usage: just `./install.sh`
#       or `./install.sh my_tasks.md` if you want to make my_tasks.md as your tasks-list by default

default_tasks_file=${1:-'tareas.md'} #  default_tasks_file will be hardcoded if $1 is non-empty.
#  even so, a tasks_file can always be passed as an argument (e.g.: `tareator tasks-myproject.md`)

cat << EOF > /tmp/tareator
#!/bin/bash

tasks_file=\`readlink -f \${1:-'$default_tasks_file'}\`

cd $(pwd)
python3 -m tareator "\$tasks_file" "\${@:2}"
#                                      ^^^ --silent flag
EOF

echo "Generating /usr/bin/tareator... (may ask for sudo password)"

sudo mv /tmp/tareator /usr/bin/tareator
sudo chmod +x /usr/bin/tareator

# if external python libraries are needed in a future,
# they can be easily virtualenv-ed here ( `python3 -m tareator "$@"` )

#tip:
# you may be interested in adding shorcuts like these to your .bash_aliases:
#
# alias tp='tareator ~/.tareator/tareas-personal.md'
# alias tt='tareator ~/.tareator/tareas-trabajo.md'
# alias tps='tareator ~/.tareator/tareas-personal.md -s'
# alias tts='tareator ~/.tareator/tareas-trabajo.md -s'
