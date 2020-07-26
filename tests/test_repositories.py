#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_list_all():
    ret = client.cmd('test.minion', 'nexus3_repositories.list_all')
    print(ret)
    assert len(ret['test.minion']['repositories']) >= 7,'not enough repositories found'


def test_hosted():
    ret = client.cmd('test.minion', 'nexus3_repositories.hosted', ['name=test-yum','format=yum','yum_repodata_depth=3','yum_deploy_policy=permissive'])
    print(ret)
    data = ret['test.minion']['repository']
    assert data['name'] == 'test-yum','wrong repo name'
    assert data['yum']['deployPolicy'] == 'PERMISSIVE','wrong deployPolicy value'
    assert data['yum']['repodataDepth'] == 3,'wrong repodataDepth value'


def test_group():
    ret = client.cmd('test.minion', 'nexus3_repositories.group', ['name=test-yum-group','format=yum','group_members=["test-yum"]'])
    print(ret)
    data = ret['test.minion']['repository']
    assert data['name'] == 'test-yum-group','wrong repository name'
    assert data['group']['memberNames'] == ['test-yum'],'wrong memberNames'


def test_describe():
    ret = client.cmd('test.minion', 'nexus3_repositories.describe', ['name=test-yum'])
    print(ret)
    assert ret['test.minion']['repository'] != {},'data is empty'
    assert ret['test.minion']['repository']['name'] == 'test-yum','repository test-yum not found'
    assert ret['test.minion']['repository']['format'] == 'yum','wrong format found'
    assert ret['test.minion']['repository']['type'] == 'hosted','wrong type found'


# clean the slate
client.cmd('test.minion', 'nexus3_repositories.delete', ['name=test-yum'])
client.cmd('test.minion', 'nexus3_repositories.delete', ['name=test-yum-group'])

test_list_all()

test_hosted()

test_group()

test_describe()