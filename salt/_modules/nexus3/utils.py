'''
Common logic used by the nexus3 state and execution module

This module contains logic to accommodate nexus3/salt CLI usage
'''

import json
import logging

import requests

log = logging.getLogger(__name__)

base_api_path = 'service/rest'


def _get_config():
    '''
    Gets configuration from minion config/pillars
    '''
    defaults = {'host':     'http://127.0.0.1:8081',
                'user':     'admin',
                'password': 'admin123'}

    # conn_info = {}
    # _opts = __salt__['config.option']('nexus3')
    # default_addrs_used = []
    # for attr in defaults:
    #     if attr not in _opts:
    #         default_addrs_used.append(attr)
    #         conn_info[attr] = defaults[attr]
    #         continue
    #     conn_info[attr] = _opts[attr]
    # if default_addrs_used:
    #     log.info('Using default value for Nexus3: {0}'.format(default_addrs_used))

    return defaults


class NexusClient:
    '''
    Class for connecting to Nexus3 APIs
    '''

    def __init__(self):
        config = _get_config()

        self.username = config['user']
        self.password = config['password']
        self.base_url = '{}/{}'.format(config['host'], base_api_path)

    def delete(self, path):
        '''
        delete object from nexus server
        '''
        delete_path = '{}/{}'.format(self.base_url, path)
        resp = False
        try:
            resp = requests.delete(delete_path, auth=(self.username, self.password))
            log.debug('NexusClient Request: {} {}'.format(delete_path, resp.status_code))
        except Exception as e:
            log.error('NexusClient Request failed: {}'.format(e))

        return resp

    def get(self, path):
        '''
        get data from nexus server
        '''
        get_path = '{}/{}'.format(self.base_url, path)
        resp = False
        try:
            resp = requests.get(get_path, auth=(self.username, self.password))
            log.debug('NexusClient Request: {} {}'.format(get_path, resp.status_code))
        except Exception as e:
            log.error('NexusClient Request failed: {}'.format(e))

        return resp

    def post(self, path, payload):
        '''
        post payload to Nexus server
        '''
        post_path = '{}/{}'.format(self.base_url, path)
        resp = False
        try:
            resp = requests.post(post_path, auth=(self.username, self.password), json=payload)
            log.debug('NexusClient Request: {} {}'.format(post_path, resp.status_code))
        except Exception as e:
            log.error('NexusClient Request failed: {}'.format(e))

        return resp

    def put(self, path, payload):
        '''
        put payload to Nexus server
        '''
        put_path = '{}/{}'.format(self.base_url, path)

        print(put_path)
        resp = False
        try:
            resp = requests.put(put_path, auth=(self.username, self.password), json=payload)
            log.debug('NexusClient Request: {} {}'.format(put_path, resp.status_code))
        except Exception as e:
            log.error('NexusClient Request failed: {}'.format(e))

        return resp