#!/bin/bash

NAME=""
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
    start $NAME
elif [[ $STOP -gt 0 ]]; then
    stop
elif [[ $RELOAD_MINION -gt 0 ]]; then
    reload $NAME
elif [[ $CMD -gt 0 ]]; then
    docker_shell
else
    usage
fi
