#!/bin/bash

# if external python libraries are needed in a future,
# they can be easily virtualenv-ed here ( "$@" )

tasks_file=${1:-'\$1'} #  tasks_file will be hardcoded if $1 is non-empty.
                       #  otherwise, it can be passed as an argument (tareator $1)

cat << EOF > /tmp/tareator
#!/bin/bash

cd $(pwd)
python3 -m tareator "$tasks_file"
EOF

echo "Generating /usr/bin/tareator... (may ask for sudo password)"

sudo mv /tmp/tareator /usr/bin/tareator
sudo chmod +x /usr/bin/tareator
