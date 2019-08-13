#!/bin/bash

echo '-------------------'
echo ' yatranslate setup '
echo '-------------------'

python_installation="ERROR"

#declare -A python=( ["0"]=`python -c 'import sys; version=sys.version_info[:3]; print("{0}".format(version[0]))' || { echo "no py"; }` ["1"]=`python -c 'import sys; version=sys.version_info[:3]; print("{0}".format(version[1]))' || { echo "no py"; }` ["2"]=`python -c 'import sys; version=sys.version_info[:3]; print("{0}".format(version[2]))' || { echo "no py"; }` )
#declare -A python3=( ["0"]=`python3 -c 'import sys; version=sys.version_info[:3]; print("{0}".format(version[1]))' || { echo "no py3"; }` ["1"]=`python3 -c 'import sys; version=sys.version_info[:3]; print("{0}".format(version[2]))' || { echo "no py3"; }` )

if hash python3.7 2>/dev/null; then
	python_installation="python3.7"
elif hash python3.6 2>/dev/null; then
	python_installation="python3.6"
elif hash python3 2>/dev/null; then
	if [ "${python3[1]}" -ge "5" ]; then # Python3 >= 3.6
		python_installation="python3"
	fi
elif hash python 2>/dev/null; then
	if [ "${python[0]}" -ge "3" ]; then # Python3 >= 3.6
		if [ "${python[1]}" -ge "5" ]; then # Python3 >= 3.6
			python_installation="python3"
		fi
	fi
fi

if [ "$python_installation" == "ERROR" ]; then
	echo "You are running an unsupported Python version."
	echo "Please use a version of Python above or equals 3.6"
	exit 1
fi

echo 'Creating virtual environment for python...'
eval "$python_installation -m venv __env"
source ./__env/bin/activate
eval "$python_installation -m pip install --upgrade pip"
eval "$python_installation -m pip install -r requirements.txt"
echo 'Done!'
echo ''

echo -e '\e[92mSetup Successful! You can start yatranslate by running:'
echo "./start.sh"
