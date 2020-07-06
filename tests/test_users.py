#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_create_users():
    ret = client.cmd('test.minion', 'nexus3_users.create', ["name=testing1", "emailAddress=fake1@email.com", "password=testpassword", "firstName=Test1", "lastName=User", "roles=['nx-admin']"])
    print(ret)
    assert ret['test.minion']['users'] != {},'users is empty'
    assert ret['test.minion']['users']['userId'] == 'testing1','userId is incorrect'
    assert ret['test.minion']['users']['firstName'] == 'Test1','firstName is incorrect'
    assert ret['test.minion']['users']['roles'] == ['nx-admin'],'roles is incorrect'

    ret = client.cmd('test.minion', 'nexus3_users.create', ["name=testing2", "emailAddress=fake2@email.com", "password=testpassword", "firstName=Test2", "lastName=User", "roles=['nx-anonymous']"])
    print(ret)
    assert ret['test.minion']['users'] != {},'users is empty'
    assert ret['test.minion']['users']['userId'] == 'testing2','userId is incorrect'
    assert ret['test.minion']['users']['roles'] == ['nx-anonymous'],'roles is incorrect'

def test_update_users():
    ret = client.cmd('test.minion', 'nexus3_users.update', ["name=testing1", "firstName=Testing", "roles=['nx-anonymous']"])
    print(ret)
    assert ret['test.minion']['users'] != {},'users is empty'
    assert ret['test.minion']['users']['firstName'] == 'Testing','firstName is incorrect'
    assert ret['test.minion']['users']['roles'] == ['nx-anonymous'],'roles is incorrect'


# clean the slate
client.cmd('test.minion', 'nexus3_users.delete', ['testing1'])
client.cmd('test.minion', 'nexus3_users.delete', ['testing2'])

test_create_users()

test_update_users()