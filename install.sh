#!/bin/bash

# if external python libraries are needed in a future,
# they can be easily virtualenv-ed here

cat << EOF > /tmp/tareas
#!/bin/bash

cd $(pwd)
python3 -m tareas "\$@"
EOF

echo "Generating /usr/bin/tareas... (may ask for sudo password)"

sudo mv /tmp/tareas /usr/bin/tareas
sudo chmod +x /usr/bin/tareas
