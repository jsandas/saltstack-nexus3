# -*- coding: utf-8 -*-
""""
State module for working with the Nexus 3 Script API

This module can be used for managing parts of Nexus that are not available in the rest api

.. note::
    Sonatype has disabled groovy script execution by default in recent versions
    of Nexus 3.  See here for defaults. 
    https://help.sonatype.com/repomanager3/rest-and-integration-api/script-api
    
Based on the work in ThoTeam's project for ansible (https://github.com/ansible-ThoTeam/nexus3-oss).
The groovy scripts used by this state are copied from or based on the scripts
provided in this repository in the nexus_groovy.py file so they sync with the
module itself.

:depends: requests

:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions otherwise defaults are used. A sample dictionary might look
    like:
    
        nexus3:
          host: '127.0.0.1:8081'
          user: 'admin'
          pass: 'admin123'


Set base url for Nexus

.. code-block:: yaml

    http://localhost:8081:
      nexus3_script.base_url

Create task for database backup
Note: The key/values under task_properties is indented 4 spaces instead
of two.  This is how salt creates a dictionary from the yaml

.. code-block:: yaml

    database_backup:
      nexus3_script.tasks:
        - task_type_id: 'db.backup'
        - task_properties:
            location:'/nexus-data/backup'
        - task_cron: '0 0 21 * * ?'
"""
# from __future__ import absolute_import, print_function, unicode_literals

import json
import logging

import requests

log = logging.getLogger(__name__)


class _ScriptClient:
    """
    Class for working with the Nexus 3 scripts API
    """

    def __init__(self, host, username, password, script_name, script_data):
        self.host = host
        self.username = username
        self.password = password
        self.script_name = script_name
        self.script_data = script_data
        self.url = '{}/service/rest/v1/script'.format(host)

    def delete(self):
        """
        Deletes script to Nexus 3 script API
        Returns false if script does not exist
        """
        delete_url = '{}/{}'.format(self.url, self.script_name)
        resp = False
        if self.get():
            log.debug('Deleting script: {}'.format(self.script_name).format(self.script_name))
            req = requests.delete(delete_url, auth=(self.username, self.password))
            if req.status_code == 204:
                resp = req.content
                return resp
            log.error('Failed deleting script: {} Reason: {}'.format(self.script_name, req.status_code))

        return resp

    def get(self):
        """
        Get script to Nexus 3 script API
        Returns false if script does not exist
        """
        get_url = '{}/{}'.format(self.url, self.script_name)
        resp = False
        try:
            log.debug('checking for script {}'.format(self.script_name))
            req = requests.get(get_url, auth=(self.username, self.password))
            if req.status_code == 200:
                resp = req.content
                return resp
            log.warning('script {} not found. response: {}'.format(self.script_name, req.status_code))
        except Exception as e:
            log.error('script {} not found. response: {}'.format(self.script_name, e))

        return resp

    def list(self):
        req = requests.get(self.url, auth=(self.username, self.password))
        resp = req.content

        return resp

    def run(self, script_args):
        """
        Runs script to Nexus 3 script API
        Returns false if script does not exist

        Results returned as null from the script API
        is actually a positive in this case
        """
        run_url = '{}/{}/run'.format(self.url, self.script_name)
        headers = {'Content-Type': 'text/plain'}
        payload = json.dumps(script_args)

        resp = False
        if self.get():
            log.debug('running script: {}'.format(self.script_name))
            req = requests.post(run_url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 200:
                resp = req.json()
                return resp
            log.error('could not run script {}. response: {}'.format(self.script_name, req.status_code))

        return resp

    def upload(self):
        """
        Uploads script to Nexus 3 script API
        If a script of the same name already exists,
        it will be updated/replaced
        """

        data = {'name': self.script_name,
                'content': self.script_data,
                'type': 'groovy'}

        payload = json.dumps(data)

        headers = {'Content-Type': 'application/json'}
        resp = False
        if self.get():
            log.debug('updating script: {}'.format(self.script_name))
            upload_url = '{}/{}'.format(self.url, self.script_name)
            req = requests.put(upload_url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 204:
                resp = True
                return resp
            log.error('could not update script {}. response: {}'.format(self.script_name, req.status_code))
        else:
            log.debug('uploading script: {}'.format(self.script_name))
            req = requests.post(self.url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 204:
                resp = True
                return resp
            log.error('could not upload script "{}." response: {}'.format(self.script_name, req.status_code))

        return resp


def _connection_info():
    '''
    Gets configuration from minion config/pillars
    '''
    conn_info = {'hostname': 'http://127.0.0.1:8081',
                'username': '',
                'password': ''}

    _opts = __salt__['config.option']('nexus3')
    
    missing_args = []
    for attr in conn_info:
        if attr not in _opts:
            missing_args.append(attr)
            continue
        conn_info[attr] = _opts[attr]

    if missing_args:
        log.error('The following connection details are missing: {}'.format(missing_args))

    return conn_info


def _script_processor(script_name, script_data, script_args, ret):
    connection_info = _connection_info()

    client = _ScriptClient(connection_info['hostname'],
                           connection_info['username'],
                           connection_info['password'],
                           script_name,
                           script_data)

    upload_results = client.upload()

    if upload_results:
        run_results = client.run(script_args)
        if run_results:
            ret['changes'] = {'nexus': run_results['result']}
        else:
            ret['result'] = False
            ret['comment'] = 'script {} failed to run. see minion logs for details.'.format(script_name)
    else:
        ret['result'] = False
        ret['comment'] = 'script {} failed to upload. see minion logs for details.'.format(script_name)

    return ret

base_url_data = """
import groovy.json.JsonSlurper

parsedArgs = new JsonSlurper().parseText(args)

core.baseUrl(parsedArgs.baseUrl)
"""

def base_url(name):
    """
    Set base url for Nexus

    Args:
        name (str):
            URL to set base_url to for Nexus 3
            This would usually be the FQDN used
            to access Nexus
    Returns:
        str: 'null' if successful
    """

    script_name = 'setup_base_url'

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'base url set: {}'.format(name)
    }

    script_args = {'baseUrl': name}

    results = _script_processor(script_name, base_url_data, script_args, ret)
    return results


task_data = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.scheduling.TaskConfiguration
import org.sonatype.nexus.scheduling.TaskInfo
import org.sonatype.nexus.scheduling.TaskScheduler
import org.sonatype.nexus.scheduling.schedule.Schedule

parsedArgs = new JsonSlurper().parseText(args)

TaskScheduler taskScheduler = container.lookup(TaskScheduler.class.getName())

TaskInfo existingTask = taskScheduler.listsTasks().find { TaskInfo taskInfo ->
    taskInfo.name == parsedArgs.name
}

if (existingTask && existingTask.getCurrentState().getRunState() != null) {
    log.info("Could not update currently running task : " + parsedArgs.name)
    return
}

TaskConfiguration taskConfiguration = taskScheduler.createTaskConfigurationInstance(parsedArgs.typeId)
if (existingTask) { taskConfiguration.setId(existingTask.getId()) }
taskConfiguration.setName(parsedArgs.name)

parsedArgs.taskProperties.each { key, value -> taskConfiguration.setString(key, value) }

if (parsedArgs.setAlertEmail) {
    taskConfiguration.setAlertEmail(parsedArgs.setAlertEmail)
}

parsedArgs.booleanTaskProperties.each { key, value -> taskConfiguration.setBoolean(key, Boolean.valueOf(value)) }

Schedule schedule = taskScheduler.scheduleFactory.cron(new Date(), parsedArgs.cron)

taskScheduler.scheduleTask(taskConfiguration, schedule)
"""

def task(name,
         typeId,
         taskProperties,
         cron,
         setAlertEmail=None):
    """
    Args:
        name (str):
            Name of task
        typeId (str):
            Nexus taskId
            Options: db.backup, repository.docker.gc, repository.docker.upload-purge,
                     blobstore.compact, repository.purge-unused
        taskProperties (dict):
            Dictionary of the task properties
        setAlertEmail (str):
            Email to send alerts to
        cron (str):
            Options: '0 0 11 * 5 ?'

            Field Name	Allowed Values
            Seconds	    0-59
            Minutes	    0-59
            Hours	    0-23
            Dayofmonth	1-31
            Month	    1-12 or JAN-DEC
            Dayofweek	1-7 or SUN-SAT
            Year(optional)	empty, 1970-2099
    Returns:
        str: metadata about task if successful
    """

    script_name = 'create_task'

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'task created/updated: {}'.format(name)}

    script_args = {'name': name,
                   'typeId': typeId,
                   'taskProperties': taskProperties,
                   'setAlertEmail': setAlertEmail,
                   'cron': cron}

    results = _script_processor(script_name, task_data, script_args, ret)

    return results
