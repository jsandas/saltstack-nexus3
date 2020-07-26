#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()


def test_configure_email():
    ret = client.cmd('test.minion', 'nexus3_email.configure', ['enabled=True',
        'host=notlocalhost','port=587','fromAddress=test@example.com','startTlsEnabled=True'])

    print(ret)
    assert ret['test.minion']['email']['host'] == 'notlocalhost','host incorrect'

    assert ret['test.minion']['email']['port'] == 587,'port incorrect'

    assert ret['test.minion']['email']['fromAddress'] == 'test@example.com','fromAddress incorrect'

    assert ret['test.minion']['email']['startTlsEnabled'] == True,'startTlsEnabled incorrect'


def test_describe_email():
    client.cmd('test.minion', 'nexus3_email.configure', ['enabled=True',
        'host=notlocalhost','port=465','fromAddress=test@example.com','sslOnConnectEnabled=True'])

    ret = client.cmd('test.minion', 'nexus3_email.describe')

    print(ret)
    assert ret['test.minion']['email']['host'] == 'notlocalhost','host incorrect'

    assert ret['test.minion']['email']['port'] == 465,'port incorrect'

    assert ret['test.minion']['email']['fromAddress'] == 'test@example.com','fromAddress incorrect'

    assert ret['test.minion']['email']['sslOnConnectEnabled'] == True,'sslOnConnectEnabled incorrect'


# clean the slate
client.cmd('test.minion', 'nexus3_email.reset')

test_configure_email()

test_describe_email()
