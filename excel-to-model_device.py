import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import json

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

USERNAME = 'admin'
PASSWORD = 'pixxpass'
IP = '127.0.0.1'
PORT = '10009'
SESSION = ''
URL = 'https://'+IP+':'+PORT+'/jsonrpc'

def login():
    payload = json.dumps({
        "session": 1,
        "id": 1,
        "method": "exec",
        "params": [{
            "url": "sys/login/user",
            "data": [{
                "user": USERNAME,
                "passwd": PASSWORD}
            ]
        }]
    })
    headers = {
        'Content-Type':'application/json'
    }

    req =  requests.request("POST", URL, headers=headers, data=payload, verify=False)
    print(req.text)
    return req
def logout():
    payload = json.dumps({
        "session": SESSION,
        "id": 1,
        "method": "exec",
        "params": [{
            "url": "sys/logout"
        }]
    })
    headers = {
        'Content-Type':'application/json'
    }
    
    req = requests.request("POST", URL, headers=headers, data=payload, verify=False)
    print(req.text)
    return req
def add_model_ha_device(adom,device_name,primary_sn,secondary_sn,device_group):
    payload = json.dumps({
      "method": "exec",
      "params": [
        {
          "data": {
            "adom": adom,
            "device": {
              "adm_usr": "admin",
              "build": 1575,
              "extra commands": [
                {
                  "method": "update",
                  "params": [
                    {
                      "url": "/pm/config/device/%s/global/system/ha",
                      "data": {
                        "password": device_name,
                        "hbdev": [
                          "ha1",
                          0,
                          "ha2",
                          0
                        ],
                        "monitor":[
                            "port12"
                        ],
                      }
                    }
                  ]
                }
              ],
              "faz.perm": 15,
              "faz.quota": 0,
              "flags": 67371040,
              "ha_group_id": 1,
              "ha_group_name": "HA",
              "ha_mode": 1,
              "ha_slave": [
                {
                  "idx": 0,
                  "sn": primary_sn,
                  "name": device_name,
                  "role": 1,
                  "prio": 200
                },
                {
                  "sn": secondary_sn,
                  "prio": 100,
                  "idx": 1,
                  "name": device_name+"-1",
                  "role": 0
                }
              ],
              "mgmt_mode": 3,
              "mr": 2,
              "name": device_name,
              "os_type": 0,
              "os_ver": 7,
              "platform_str": "FortiGate-100F",
              "prefer_img_ver": "7.2.6-b1575",
              "sn": primary_sn,
              "version": 700
            },
            "flags": [
              "create_task"
            ],
            "groups":[
                { "name": device_group }
            ]
          },
          "url": "/dvm/cmd/add/device"
        }
      ],
      "session": SESSION,
      "id": 1
    })
    headers = {
      'Content-Type': 'application/json'
    }

    req = requests.request("POST", URL, headers=headers, data=payload, verify=False)
    print(req.text)
def attach_prerun_template(adom,device_name,pre_run_template):
    payload = json.dumps({
      "method": "add",
      "params": [
        {
          "data": {
            "name": device_name,
            "vdom": "global"
          },
          "url": "/pm/config/adom/"+adom+"/obj/cli/template/"+pre_run_template+"/scope member"
        }
      ],
      "session": SESSION,
      "id": 1
    })
    headers = {
      'Content-Type': 'application/json'
    }

    req = requests.request("POST", URL, headers=headers, data=payload, verify=False)
    print(req.text)
def update_metadata(adom,device_name,params):
    query = {
      "method": "add",
      "params": [],
      "session": SESSION,
      "id": 1
    }
    
    for key,value in params.items():
        metadata_query = {
          "data": {
            "_scope": [
              {
                "name": device_name,
                "vdom": "global"
              }
            ],
            "value": str(value)
          },
          "url": "/pm/config/adom/"+adom+"/obj/fmg/variable/"+key+"/dynamic_mapping"
        }
        query['params'].append(metadata_query)

    payload = json.dumps(query)
    headers = {
      'Content-Type': 'application/json'
    }

    req = requests.request("POST", URL, headers=headers, data=payload, verify=False)
    print(req.text)

## Reading Excel Configuration
config_file = pd.ExcelFile('device_list.xlsx')
standalone_file = pd.read_excel(config_file,'standalone')
ha_file = pd.read_excel(config_file,'ha')

# Login to the FortiManager and get the session
SESSION = json.loads(login().text)['session']

## adding Standalone FortiGates
#for x in standalone_file.to_dict(orient='records'):
#    adom = x['adom']

## adding HA FortiGates
for device in ha_file.to_dict(orient='records'):
    adom = device['adom']
    device_name = device['device_name']
    primary_sn = device['primary_sn']
    secondary_sn = device['secondary_sn']
    device_group = device['device_group']
    pre_run_template = device['pre_run_template']
    params = {
        'is_ha': device['is_ha'],
        'ha_mgmt_interface': device['ha_mgmt_interface'],
        'ha_mgmt_ip': device['ha_mgmt_ip'],
        'mgmt_gateway': device['mgmt_gateway']
    }

    add_model_ha_device(adom,device_name,primary_sn,secondary_sn,device_group)
    attach_prerun_template(adom,device_name,pre_run_template)
    update_metadata(adom,device_name,params)

# logout
logout()