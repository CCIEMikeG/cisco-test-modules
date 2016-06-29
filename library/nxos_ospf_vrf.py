#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: nxos_ospf_vrf
version_added: "2.2"
short_description: Manages a VRF for an OSPF router.
description:
    - Manages a VRF for an OSPF router.
author: Gabriele Gerbino (@GGabriele)
extends_documentation_fragment: nxos
notes:
    - 'default' restores params default value
options:
    vrf:
        description:
            - Name of the resource instance. Valid value is a string.
              The name 'default' is a valid VRF representing the global ospf.
        required: false
        default: default
    ospf:
        description:
            - Name of the ospf instance.
        required: true
        default: null
    router_id:
        description:
            - Router Identifier (ID) of the OSPF router VRF instance.
        required: false
        default: null
    m_facts:
        description:
            - Used to print module facts
        required: false
        default: false
        choices: ['true','false']
'''
EXAMPLES = '''
- nxos_ospf_vrf:
    ospf: 1
    router_id: "2.2.2.2"
'''

PARAM_TO_COMMAND_KEYMAP = {
    'router_id': 'router-id',
}
PARAM_TO_DEFAULT_KEYMAP = {}


def invoke(name, *args, **kwargs):
    func = globals().get(name)
    if func:
        return func(*args, **kwargs)


def get_value(arg, config, module):
    REGEX = re.compile(r'(?:{0}\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
    value = ''
    if PARAM_TO_COMMAND_KEYMAP[arg] in config:
        value = REGEX.search(config).group('value')
    return value


def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)
    parents = ['router ospf {0}'.format(module.params['ospf'])]

    if module.params['vrf'] != 'default':
        parents.append('vrf {0}'.format(module.params['vrf']))

    config = netcfg.get_section(parents)

    if config:
        if module.params['vrf'] == 'default':
            splitted_config = config.splitlines()
            vrf_index = False
            for index in range(0, len(splitted_config) - 1):
                if 'vrf' in splitted_config[index].strip():
                        vrf_index = index
                        break
            if vrf_index:
                config = '\n'.join(splitted_config[0:vrf_index])

        for arg in args:
            if arg not in ['ospf', 'vrf']:
                existing[arg] = get_value(arg, config, module)

        existing['vrf'] = module.params['vrf']
        existing['ospf'] = module.params['ospf']

    return existing


def apply_key_map(key_map, table):
    new_dict = {}
    for key, value in table.items():
        new_key = key_map.get(key)
        if new_key:
            value = table.get(key)
            if value:
                new_dict[new_key] = value
            else:
                new_dict[new_key] = value
    return new_dict


def state_present(module, existing, proposed, candidate):
    commands = list()
    proposed_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, proposed)
    existing_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, existing)

    for key, value in proposed_commands.iteritems():
        if value is True:
            commands.append(key)

        elif value is False:
            commands.append('no {0}'.format(key))

        elif value == 'default':
            if existing_commands.get(key):
                existing_value = existing_commands.get(key)
                commands.append('no {0} {1}'.format(key, existing_value))
        else:
            command = '{0} {1}'.format(key, value.lower())
            commands.append(command)

    if commands:
        parents = ['router ospf {0}'.format(module.params['ospf'])]
        if module.params['vrf'] != 'default':
            parents.append('vrf {0}'.format(module.params['vrf']))

        candidate.add(commands, parents=parents)


def state_absent(module, existing, proposed, candidate):
    commands = []
    parents = ['router ospf {0}'.format(module.params['ospf'])]
    if module.params['vrf'] == 'default':
        existing_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, existing)
        for key, value in existing_commands.iteritems():
            if value:
                existing_value = existing_commands.get(key)
                commands.append('no {0} {1}'.format(key, existing_value))
    else:
        commands = ['no vrf {0}'.format(module.params['vrf'])]

    candidate.add(commands, parents=parents)


def main():
    argument_spec = dict(
            vrf=dict(required=False, type='str', default='default'),
            ospf=dict(required=True, type='str'),
            router_id=dict(required=False, type='str'),
            m_facts=dict(required=False, default=False, type='bool'),
            state=dict(choices=['present', 'absent'], default='present',
                       required=False),
    )
    argument_spec.update(nxos_argument_spec)
    module = get_module(argument_spec=argument_spec,
                        supports_check_mode=True)

    state = module.params['state']

    args =  [
            'vrf',
            'ospf',
            'router_id',
        ]

    existing = invoke('get_existing', module, args)
    end_state = existing
    proposed_args = dict((k, v) for k, v in module.params.iteritems()
                    if v is not None and k in args)

    proposed = {}
    for key, value in proposed_args.iteritems():
        if key != 'interface':
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.lower() == 'default':
                value = PARAM_TO_DEFAULT_KEYMAP.get(key)
                if value is None:
                    value = 'default'
            if existing.get(key) or (not existing.get(key) and value):
                proposed[key] = value

    result = {}
    if state == 'present' or (state == 'absent' and existing):
        candidate = NetworkConfig(indent=3)
        invoke('state_%s' % state, module, existing, proposed, candidate)

        try:
            response = load_config(module, candidate)
            result.update(response)
        except NetworkError:
            exc = get_exception()
            module.fail_json(msg=str(exc))
    else:
        result['updates'] = []

    result['connected'] = module.connected
    if module.params['m_facts']:
        end_state = invoke('get_existing', module, args)
        result['end_state'] = end_state
        result['existing'] = existing
        result['proposed'] = proposed_args

    module.exit_json(**result)


from ansible.module_utils.netcfg import *
from ansible.module_utils.netcmd import *
from ansible.module_utils.nxos import *

if __name__ == '__main__':
    main()
