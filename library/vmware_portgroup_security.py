#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, sky_joker
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION='''
module: vmware_portgroup_security
short_description: module to change security settings of PortGroup.
description:
    - Promiscuous mode setting can be changed of PortGroup.
    - Mac address changes setting can be changed of PortGroup.
    - Forged transmits setting can be changed of PortGroup.
requirements:
    - python >= 2.6
    - pyVmomi
options:
    esxi_hostname:
        description:
            - Specify ESXi to be changed.
        required: True
    pg_name:
        description:
            - Specify PortGroup name to be changed.
        required: True
    promiscuous_mode:
        description:
            - Specify True to enable Accept.
            - Specify False to enable Reject.
            - Specify Null for Inherit from vSwitch.
        choices: [True, False, Null]
    mac_address_changes:
        description:
            - Specify True to enable Accept.
            - Specify False to enable Reject.
            - Specify Null for Inherit from vSwitch.
        choices: [True, False, Null]
    forged_transmits:
        description:
            - Specify True to enable Accept.
            - Specify False to enable Reject.
            - Specify Null for Inherit from vSwitch.
        choices: [True, False, Null]
'''

EXAMPLES='''
---
- name: Example of accept promiscuous_mode.
  vmware_portgroup_security:
    hostname: vCenter or ESXi
    username: username
    password: secret
    validate_certs: no
    esxi_hostname: esxi-03.local
    pg_name: VM Network
    promiscuous_mode: yes
    
- name: Example of reject promiscuous_mode.
  vmware_portgroup_security:
    hostname: vCenter or ESXi
    username: username
    password: secret
    validate_certs: no
    esxi_hostname: esxi-03.local
    pg_name: VM Network
    promiscuous_mode: no

- name: Example of inherit promiscuous_mode.
  vmware_portgroup_security:
    hostname: vCenter or ESXi
    username: username
    password: secret
    validate_certs: no
    esxi_hostname: esxi-03.local
    pg_name: VM Network
    promiscuous_mode: Null

- name: Example of changing all modes.
  vmware_portgroup_security:
    hostname: vCenter or ESXi
    username: username
    password: secret
    validate_certs: no
    esxi_hostname: esxi-03.local
    pg_name: VM Network
    promiscuous_mode: yes
    mac_address_changes: no
    forged_transmits: Null
'''

try:
    from pyVmomi import vim, vmodl
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

from ansible.module_utils.vmware import find_obj, connect_to_api, vmware_argument_spec, wait_for_task
from ansible.module_utils.basic import AnsibleModule

class VMwarePortGroupSecurity():
    def __init__(self, module):
        self.module = module
        self.esxi_hostname = module.params['esxi_hostname']
        self.pg_name = module.params['pg_name']
        self.promiscuous_mode = module.params['promiscuous_mode']
        self.mac_address_changes = module.params['mac_address_changes']
        self.forged_transmits = module.params['forged_transmits']
        self.content = connect_to_api(module)

    def execute(self):
        result = dict(changed=False)

        obj = find_obj(self.content, [vim.HostSystem], self.esxi_hostname)
        if(obj):
            for pg in obj.config.network.portgroup:
                if (isinstance(pg, vim.host.PortGroup) and pg.spec.name == self.pg_name):
                    portgroup_spec = pg.spec
                    portgroup_spec.policy.security.allowPromiscuous = self.promiscuous_mode
                    portgroup_spec.policy.security.forgedTransmits = self.forged_transmits
                    portgroup_spec.policy.security.macChanges = self.mac_address_changes

                    try:
                        obj.configManager.networkSystem.UpdatePortGroup(self.pg_name, portgroup_spec)
                    except:
                        self.module.fail_json(msg="Failed to portgroup security update %s." % self.pg_name)

                    result['changed'] = True
                    self.module.exit_json(**result)
                else:
                    self.module.fail_json(msg="%s not found" % self.pg_name)
        else:
            self.module.fail_json(msg="%s not found." % self.esxi_hostname)

def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(esxi_hostname=dict(type=str, required=True),
                         pg_name=dict(type=str, required=True),
                         promiscuous_mode=dict(choices=[True, False, None]),
                         mac_address_changes=dict(choices=[True, False, None]),
                         forged_transmits=dict(choices=[True, False, None]))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if (not (HAS_PYVMOMI)):
        module.fail_json(msg="pyvmomi is required for this module")

    vmware_portgroup_security = VMwarePortGroupSecurity(module)
    vmware_portgroup_security.execute()

if __name__ == "__main__":
    main()
