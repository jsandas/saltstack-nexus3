#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_describe_anonymous_access():
    ret = client.cmd('test.minion', 'nexus3_anonymous_access.describe')
    print(ret)
    assert ret['test.minion']['anonymous_access'] != {},'anonymous_access is empty'
    assert ret['test.minion']['anonymous_access']['enabled'] == False,'anonymous_access should be disabled'


def test_update_anonymous_access():
    ret = client.cmd('test.minion', 'nexus3_anonymous_access.update', ['enabled=True'])
    print(ret)
    assert ret['test.minion']['anonymous_access'] != {},'anonymous_access is empty'
    assert ret['test.minion']['anonymous_access']['enabled'] == True,'anonymous_access should be enabled'


# clean the slate
client.cmd('test.minion', 'nexus3_anonymous_access.update', ['enabled=False'])

test_describe_anonymous_access()

test_update_anonymous_access()
