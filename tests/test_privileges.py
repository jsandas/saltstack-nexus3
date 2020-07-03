#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_create_privileges():
    ret = client.cmd('test.minion', 'nexus3_privileges.create', ["name=testing1", "actions=['ADD','READ']", "description='Change password permission'", "domain=userschangepw", "privilege_type=application"])
    print(ret)
    assert ret['test.minion']['privilege'] != {},'privilege is empty'
    assert ret['test.minion']['privilege']['name'] == 'testing1','privilege name is incorrect'
    assert ret['test.minion']['privilege']['actions'] == ['ADD','READ'],'privilege action is incorrect'
    assert ret['test.minion']['privilege']['domain'] == 'userschangepw','privilege domain is incorrect'
    assert ret['test.minion']['privilege']['type'] == 'application','privilege privilege is incorrect'

    ret = client.cmd('test.minion', 'nexus3_privileges.create', ["name=testing2", "actions=['ALL']", "description='Test repo admin'", "format=maven2", "repository=*", "privilege_type=repository-admin"])
    print(ret)
    assert ret['test.minion']['privilege'] != {},'privilege is empty'
    assert ret['test.minion']['privilege']['name'] == 'testing2','privilege name is incorrect'
    assert ret['test.minion']['privilege']['actions'] == ['ALL'],'privilege action is incorrect'
    assert ret['test.minion']['privilege']['format'] == 'maven2','privilege format is incorrect'
    assert ret['test.minion']['privilege']['repository'] == '*','privilege repository is incorrect'


def test_update_privileges():
    ret = client.cmd('test.minion', 'nexus3_privileges.update', ["name=testing1", "description='New Description'", "domain=users"])
    print(ret)
    assert ret['test.minion']['privilege'] != {},'privilege is empty'
    assert ret['test.minion']['privilege']['description'] == 'New Description','privilege description is incorrect'
    assert ret['test.minion']['privilege']['domain'] == 'users','privilege domain is incorrect'

    ret = client.cmd('test.minion', 'nexus3_privileges.update', ["name=testing3", "description='New Description'", "domain=users"])
    print(ret)
    assert ret['test.minion']['error'] != '','should have had error empty'


# clean the slate
client.cmd('test.minion', 'nexus3_privileges.delete', ['name=testing1'])
client.cmd('test.minion', 'nexus3_privileges.delete', ['name=testing2'])

test_create_privileges()

test_update_privileges()