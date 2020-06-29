#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_update_realms():
    ret = client.cmd('test.minion', 'nexus3_realms.update', [['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken']])
    print(ret)
    assert ret['test.minion']['realms'] != {},'realms is empty'
    assert ret['test.minion']['realms']== ['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken'],'realms is incorrect'


def test_active_realms():
    client.cmd('test.minion', 'nexus3_realms.update', [['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken','NpmToken']])
    ret = client.cmd('test.minion', 'nexus3_realms.list_active')
    print(ret)
    assert ret['test.minion']['realms'] != {},'realms is empty'
    assert ret['test.minion']['realms'] == ['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken','NpmToken'],'realms is incorrect'


# clean the slate
client.cmd('test.minion', 'nexus3_realms.reset')

test_update_realms()

test_active_realms()