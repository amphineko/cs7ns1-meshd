echo "Creating nodes running in background"
for (( i=0; i<=3; i++ ))
do
    nohup python3 daemon.py </dev/null >/dev/null 2>&1 &
done

echo "Creating a node in foreground"
python3 daemon.py
