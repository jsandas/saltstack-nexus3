Testing

Start salt test env
```bash
./salt-env.sh start
```
Wait for admin password to be printed on screen
```bash
Pulling salt-master ... done
Pulling nexus3      ... done
Pulling salt-minion ... done
salt-master is up-to-date
nexus3 is up-to-date
salt-minion is up-to-date

 Waiting for admin.password to be generated
admin password: 95ed2dbd-2d30-4ca0-a4e8-321eec421307
```

Use temp admin password to login into Nexus http://localhost:8081

Set admin password to "admin123"

Log out of Nexus 3

Switch to cli in salt-master container
```bash
./salt-env.sh cmd
```

Test module
```bash
salt \* nexus3_repositories.list_all
```

Note: running start again after setting the new admin password will cause it to fail
    to retrieve the temp admin password, but is not an issue