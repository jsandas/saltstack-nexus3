#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()

def test_create_blobstore():

    ret = client.cmd('test.minion', 'nexus3.create_blobstore', ['name=test1'])

    print(ret)
    assert ret['test.minion']['blobstore'] != {},'blobstore is empty'

    assert ret['test.minion']['blobstore']['name'] == 'test1','blobstore test1 not created'

    assert ret['test.minion']['blobstore']['type'] == 'File','wrong store type found'

    ret = client.cmd('test.minion', 'nexus3.create_blobstore', ['name=test2'])

    print(ret)
    assert ret['test.minion']['blobstore'] != {},'blobstore is empty'

    assert ret['test.minion']['blobstore']['name'] == 'test2','blobstore test2 not created'

    assert ret['test.minion']['blobstore']['type'] == 'File','wrong store type found'


def test_update_blobstore():
    ret = client.cmd('test.minion', 'nexus3.update_blobstore', ['name=test1','quota_type=spaceRemainingQuota','quota_limit=5000000'])

    print(ret)
    assert ret['test.minion']['blobstore'] != {},'data is empty'

    assert ret['test.minion']['blobstore']['name'] == 'test1','blobstore test1 not found'

    assert ret['test.minion']['blobstore']['softQuota']['type'] == 'spaceRemainingQuota','wrong quota type found'

    assert ret['test.minion']['blobstore']['softQuota']['limit'] == 5000000,'wrong quota limit found'


def test_describe_blobstore():
    ret = client.cmd('test.minion', 'nexus3.describe_blobstore', ['name=test1'])

    print(ret)
    assert ret['test.minion']['blobstore'] != {},'data is empty'

    assert ret['test.minion']['blobstore']['name'] == 'test1','blobstore test1 not found'

    assert ret['test.minion']['blobstore']['type'] == 'File','wrong store type found'


def test_list_blobstores():
    ret = client.cmd('test.minion', 'nexus3.list_blobstores')

    print(ret)
    assert ret['test.minion']['blobstore'] != {},'data is empty'

    # this test is brittle as it assumes no other blobstores exists
    # in the nexus instance being tested
    # there should be three blobstores: default, test1, and test2
    # assert len(ret['test.minion']['blobstore']) == 3,'incorrect blobstore count'


def test_delete_blobstore():
    ret = client.cmd('test.minion', 'nexus3.delete_blobstore', ['name=test1'])
    print(ret)
    assert ret['test.minion']['coment'] == 'Deleted blobstore "test1"','blobstore test1 not deleted'

    ret = client.cmd('test.minion', 'nexus3.delete_blobstore', ['name=test2'])
    print(ret)
    assert ret['test.minion']['coment'] == 'Deleted blobstore "test2"','blobstore test2 not deleted'


# clean the slate
client.cmd('test.minion', 'nexus3.delete_blobstore', ['name=test1'])
client.cmd('test.minion', 'nexus3.delete_blobstore', ['name=test2'])

test_create_blobstore()

test_update_blobstore()

test_describe_blobstore()

test_list_blobstores()

test_delete_blobstore()