DIRECTORY=$(cd `dirname $0` && pwd)
echo $DIRECTORY
cd $DIRECTORY

git fetch
python $DIRECTORY/SaarFlask/app.py
read 