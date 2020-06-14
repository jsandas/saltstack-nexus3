#!/usr/bin/env python

import salt.client

client = salt.client.LocalClient()


def test_configure_email():
    ret = client.cmd('test.minion', 'nexus3.configure_email', ['enabled=True',
        'host=notlocalhost','port=587','email_from=test@example.com','starttls_enabled=True'])

    print(ret)
    assert ret['test.minion']['email']['host'] == 'notlocalhost','host incorrect'

    assert ret['test.minion']['email']['port'] == 587,'port incorrect'

    assert ret['test.minion']['email']['fromAddress'] == 'test@example.com','email_from incorrect'

    assert ret['test.minion']['email']['startTlsEnabled'] == True,'starttls_enabled incorrect'


def test_describe_email():
    client.cmd('test.minion', 'nexus3.configure_email', ['enabled=True',
        'host=notlocalhost','port=465','email_from=test@example.com','tls_connect=True'])

    ret = client.cmd('test.minion', 'nexus3.describe_email')

    print(ret)
    assert ret['test.minion']['email']['host'] == 'notlocalhost','host incorrect'

    assert ret['test.minion']['email']['port'] == 465,'port incorrect'

    assert ret['test.minion']['email']['fromAddress'] == 'test@example.com','email_from incorrect'

    assert ret['test.minion']['email']['sslOnConnectEnabled'] == True,'tls_connect incorrect'


# clean the slate
client.cmd('test.minion', 'nexus3.configure_email')

test_configure_email()

test_describe_email()
