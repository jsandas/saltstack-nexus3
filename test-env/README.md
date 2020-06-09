Testing

Start salt test env
```bash
./salt-env.sh start
```

Switch to cli in salt-master container
```bash
./salt-env.sh cmd
```

Deply Nexus
```bash
salt \* state.apply nexus
```

Get temp admin password
```bash
salt \* cmd.run "cat /data/nexus/admin.password"
```

Use temp admin password to login into Nexus http://localhost:8081

Set admin password to "admin123" or something else and update