#!/bin/bash

START=0
STOP=0
RELOAD_MINION=0
CMD=0

docker_shell () {
    docker exec -it salt-master ash
}
    
start () {
    docker-compose pull
    docker-compose up -d
    
    # sync salt files for the first time
    docker exec salt-master sh -c 'salt \* saltutil.sync_all' > /dev/null 2>&1

    printf "\n Waiting for admin.password to be generated"
    _dur=0
    until docker exec nexus3 bash -c 'test -f /nexus-data/admin.password'
    do
        if [ $_dur -gt 30 ]; then
            echo "Couldn't get admin password"
            exit 1
        fi
        _dur=$((_dur+1))
        sleep 1
        echo -ne "."
    done
    
    printf "\nadmin password: $(docker exec nexus3 bash -c 'cat /nexus-data/admin.password')\n"
}

stop () {
    docker-compose down
}

reload () {
    docker exec -it salt-master salt-key -D -y
    docker rm -f salt-minion
    docker-compose up -d    
}

usage () {
    echo "invalid input"
    echo " Usage:" 
    echo " ./salt-env (start|stop|reload|cmd) ARGS"
    echo ""
}

while [[ $# -gt 0 ]]
do
    key=$1
    case "$key" in
        start)
        START=1
        shift # past argument
        ;;
        stop)
        STOP=1
        shift # past argument
        ;;
        reload)
        RELOAD_MINION=1
        shift # past argument
        ;;
        cmd)
        CMD=1
        shift # past argument
        ;;
    esac
done

if [[ $START -gt 0 ]]; then
    start
elif [[ $STOP -gt 0 ]]; then
    stop
elif [[ $RELOAD_MINION -gt 0 ]]; then
    reload
elif [[ $CMD -gt 0 ]]; then
    docker_shell
else
    usage
fi