#!/bin/bash

# if external python libraries are needed in a future,
# they can be easily virtualenv-ed here

cat << EOF > /tmp/tareator
#!/bin/bash

cd $(pwd)
python3 -m tareator "\$@"
EOF

echo "Generating /usr/bin/tareator... (may ask for sudo password)"

sudo mv /tmp/tareator /usr/bin/tareator
sudo chmod +x /usr/bin/tareator
