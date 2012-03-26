#!/usr/bin/env bash
#
# Run the project tests
# 
# There are lots of options for nose - run './manage.py test --help' to see them

echo "RUNNING TESTS"
echo "============="

# Change to directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Use below to show deprecation warnings
python manage.py test --settings=settings_test -v 2 

# Print out a nice colored message
if [ $? -eq 0 ]; then
	echo -e "\033[42;37mTests passed!\033[0m"
else
	echo -e "\033[41;37mTests failed!\033[0m"
fi
