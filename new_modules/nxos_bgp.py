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
module: nxos_bgp
version_added: "2.2"
short_description: Manages BGP configuration
description:
    - Manages BGP configurations on NX-OS switches
author: Jason Edelman (@jedelman8), Gabriele Gerbino (@GGabriele)
extends_documentation_fragment: nxos
notes:
    - State 'absent' removes the whole BGP ASN configuration when VRF is
      'default' or the whole VRF instance within the BGP process when using
      a different VRF.
    - 'default' restores params default value
    - Configuring global parmas is only permitted if VRF is 'default'
options:
    asn:
        description:
            - BGP autonomous system number. Valid values are String,
              Integer in ASPLAIN or ASDOT notation.
        required: true
    vrf:
        description:
            - Name of the VRF. The name 'default' is a valid VRF representing the global bgp.
        required: false
        default: null
    bestpath_always_compare_med:
        description:
            - Enable/Disable MED comparison on paths from different autonomous systems
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_aspath_multipath_relax:
        description:
            - Enable/Disable load sharing across the providers with
              different (but equal-length) AS paths.
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_compare_routerid:
        description:
            - Enable/Disable comparison of router IDs for identical eBGP paths.
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_cost_community_ignore:
        description:
            - Enable/Disable Ignores the cost community for BGP best-path calculations.
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_med_confed:
        description:
            - Enable/Disable enforcement of bestpath to do a MED comparison
              only between paths originated within a confederation.
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_med_missing_as_worst:
        description:
            - Enable/Disable assigns the value of infinity to received routes that
              do not carry the MED attribute, making these routes the least desirable.
        required: false
        choices: ['true','false', 'default']
        default: null
    bestpath_med_non_deterministic:
        description:
            - Enable/Disable deterministic selection of the best MED path from among
              the paths from the same autonomous system.
        required: false
        choices: ['true','false', 'default']
        default: null
    cluster_id:
        description:
            - Route Reflector Cluster-ID
        required: false
        default: null
    confederation_id:
        description:
            - Routing domain confederation AS
        required: false
        default: null
    confederation_peers:
        description:
            - AS confederation parameters
        required: false
        default: null
    disable_policy_batching:
        description:
            - Enable/Disable the batching evaluation of prefix advertisements to all peers.
        required: false
        choices: ['true','false', 'default']
        default: null
    disable_policy_batching_ipv4_prefix_list:
        description:
            - Enable/Disable the batching evaluation of prefix advertisements to all
              peers with prefix list
        required: false
        default: null
    disable_policy_batching_ipv6_prefix_list:
        description:
            - Enable/Disable the batching evaluation of prefix advertisements to all peers with prefix list
        required: false
    enforce_first_as:
        description:
            - Enable/Disable enforces the neighbor autonomous system to be the first AS number
              listed in the AS path attribute for eBGP.  On NX-OS, this property is only supported
              in the global BGP context.
        required: false
        choices: ['true','false', 'default']
        default: null
    event_history_cli:
        description:
            - Enable/Disable cli event history buffer.
        required: false
        choices: ['size_small', 'size_medium', 'size_large', 'size_disable', 'default']
        default: null
    event_history_detail:
        description:
            - Enable/Disable detail event history buffer.
        required: false
        choices: ['size_small', 'size_medium', 'size_large', 'size_disable', 'default']
        default: null
    event_history_events:
        description:
            - Enable/Disable event history buffer.
        required: false
        choices: ['size_small', 'size_medium', 'size_large', 'size_disable', 'default']
        default: null
    event_history_periodic:
        description:
            - Enable/Disable periodic event history buffer.
        required: false
        choices: ['size_small', 'size_medium', 'size_large', 'size_disable', 'default']
    fast_external_fallover:
        description:
            - Enable/Disable immediately reset the session if the link to a
              directly connected BGP peer goes down.  Only supported in the global BGP context.
        required: false
        choices: ['true','false', 'default']
        default: null
    flush_routes:
        description:
            - Enable/Disable flush routes in RIB upon controlled restart.
              On NX-OS, this property is only supported in the global BGP context.
        required: false
        choices: ['true','false', 'default']
        default: null
    graceful_restart:
        description:
            - Enable/Disable graceful restart
        required: false
        choices: ['true','false', 'default']
        default: null
    graceful_restart_helper:
        description:
            - Enable/Disable graceful restart helper mode
        required: false
        choices: ['true','false', 'default']
        default: null
    graceful_restart_timers_restart:
        description:
            - Set maximum time for a restart sent to the BGP peer
        required: false
        choices: ['true','false', 'default']
        default: null
    graceful_restart_timers_stalepath_time:
        description:
            - Set maximum time that BGP keeps the stale routes from the restarting BGP peer
        choices: ['true','false', 'default']
        default: null
    isolate:
        description:
            - Enable/Disable isolate this router from BGP perspective.
        required: false
        choices: ['true','false', 'default']
        default: null
    local_as:
        description:
            - Local AS number to be used within a VRF instance
        required: false
        choices: string
        default: null
    log_neighbor_changes:
        description:
            - Enable/Disable message logging for neighbor up/down event.
        required: false
        choices: ['true','false', 'default']
        default: null
    maxas_limit:
        description:
            - Specify Maximum number of AS numbers allowed in the AS-path attribute
              Valid values are between 1 and 512.
        required: false
        default: null
    neighbor_down_fib_accelerate:
        description:
            - Enable/Disable handle BGP neighbor down event, due to various reasons.
        required: false
        choices: ['true','false', 'default']
        default: null
    reconnect_interval:
        description:
            - The BGP reconnection interval for dropped sessions.  1 - 60.
        required: false
        default: null
    router_id:
        description:
            - Router Identifier (ID) of the BGP router VRF instance
        required: false
        default: null
    shutdown:
        description:
            - Administratively shutdown the BGP protocol.
        required: false
        choices: ['true','false', 'default']
        default: null
    suppress_fib_pending:
        description:
            - Enable/Disable advertise only routes programmed in hardware to peers.
        required: false
        choices: ['true','false', 'default']
        default: null
    timer_bestpath_limit:
        description:
            - Specify timeout for the first best path after a restart, in seconds
        required: false
        default: null
    timer_bestpath_limit_always:
        description:
            - Enable/Disable update-delay-always option.
        required: false
        choices: ['true','false', 'default']
        default: null
    timer_bgp_hold:
        description:
            - Set bgp hold timer
        required: false
        default: null
    timer_bgp_keepalive:
        description:
            - Set bgp keepalive timer.
        required: false
        default: null
    state:
        description:
            - Determines whether the config should be present or not on the device.
        required: false
        default: present
        choices: ['present','absent']
    m_facts:
        description:
            - Used to print module facts
        required: false
        default: false
        choices: ['true','false']
'''


EXAMPLES = '''
# configure a simple asn
- nxos_bgp:
      asn=65535
      vrf=default
      state=present
      transport=cli
'''


import re

ACCEPTED = ['true','false', 'default']
BOOL_PARAMS = [
    'bestpath_always_compare_med',
    'bestpath_aspath_multipath_relax',
    'bestpath_compare_neighborid',
    'bestpath_compare_routerid',
    'bestpath_cost_community_ignore',
    'bestpath_med_confed',
    'bestpath_med_missing_as_worst',
    'bestpath_med_non_deterministic',
    'disable_policy_batching',
    'enforce_first_as',
    'fast_external_fallover',
    'flush_routes',
    'graceful_restart',
    'graceful_restart_helper',
    'isolate',
    'log_neighbor_changes',
    'neighbor_down_fib_accelerate',
    'shutdown',
    'suppress_fib_pending'
]
GLOBAL_PARAMS = [
    'disable_policy_batching',
    'disable_policy_batching_ipv4_prefix_list',
    'disable_policy_batching_ipv6_prefix_list',
    'enforce_first_as',
    'event_history_cli',
    'event_history_detail',
    'event_history_events',
    'event_history_periodic',
    'fast_external_fallover',
    'flush_routes',
    'isolate',
    'shutdown'
]
PARAM_TO_DEFAULT_KEYMAP = {
    'timer_bgp_keepalive': '60',
    'timer_bgp_hold': '180',
    'timer_bestpath_limit': '300',
    'graceful_restart': True,
    'graceful_restart_timers_restart': '120',
    'graceful_restart_timers_stalepath_time': '300',
    'reconnect_interval': '60',
    'suppress_fib_pending': True,
    'fast_external_fallover': True,
    'enforce_first_as': True,
    'event_history_periodic': True,
    'event_history_cli': True,
    'event_history_events': True
}
PARAM_TO_COMMAND_KEYMAP = {
    'asn': 'router bgp',
    'bestpath_always_compare_med': 'bestpath always-compare-med',
    'bestpath_aspath_multipath_relax': 'bestpath as-path multipath-relax',
    'bestpath_compare_neighborid': 'bestpath compare-neighborid',
    'bestpath_compare_routerid': 'bestpath compare-routerid',
    'bestpath_cost_community_ignore': 'bestpath cost-community ignore',
    'bestpath_med_confed': 'bestpath med confed',
    'bestpath_med_missing_as_worst': 'bestpath med missing-as-worst',
    'bestpath_med_non_deterministic': 'bestpath med non-deterministic',
    'cluster_id': 'cluster-id',
    'confederation_id': 'confederation identifier',
    'confederation_peers': 'confederation peers',
    'disable_policy_batching': 'disable-policy-batching',
    'disable_policy_batching_ipv4_prefix_list': 'disable-policy-batching ipv4 prefix-list',
    'disable_policy_batching_ipv6_prefix_list': 'disable-policy-batching ipv6 prefix-list',
    'enforce_first_as': 'enforce-first-as',
    'event_history_cli': 'event-history cli',
    'event_history_detail': 'event-history detail',
    'event_history_events': 'event-history events',
    'event_history_periodic': 'event-history periodic',
    'fast_external_fallover': 'fast-external-fallover',
    'flush_routes': 'flush-routes',
    'graceful_restart': 'graceful-restart',
    'graceful_restart_helper': 'graceful-restart-helper',
    'graceful_restart_timers_restart': 'graceful-restart restart-time',
    'graceful_restart_timers_stalepath_time': 'graceful-restart stalepath-time',
    'isolate': 'isolate',
    'local_as': 'local-as',
    'log_neighbor_changes': 'log-neighbor-changes',
    'maxas_limit': 'maxas-limit',
    'neighbor_down_fib_accelerate': 'neighbor-down fib-accelerate',
    'reconnect_interval': 'reconnect-interval',
    'router_id': 'router-id',
    'shutdown': 'shutdown',
    'suppress_fib_pending': 'suppress-fib-pending',
    'timer_bestpath_limit': 'timers bestpath-limit',
    'timer_bgp_hold': 'timer bgp',
    'timer_bgp_keepalive': 'timer bpg',
    'vrf': 'vrf'
}


def invoke(name, *args, **kwargs):
    func = globals().get(name)
    if func:
        return func(*args, **kwargs)


def get_custom_value(config, arg):
    if arg.startswith('event_history'):
        REGEX_SIZE = re.compile(r'(?:{0} size\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        REGEX = re.compile(r'\s+{0}\s*$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = False

        if 'no {0}'.format(PARAM_TO_COMMAND_KEYMAP[arg]) in config:
            pass
        elif PARAM_TO_COMMAND_KEYMAP[arg] in config:
            try:
                value = REGEX_SIZE.search(config).group('value')
            except AttributeError:
                if REGEX.search(config):
                    value = True

    elif arg == 'confederation_peers':
        REGEX = re.compile(r'(?:confederation peers\s)(?P<value>.*)$', re.M)
        value = ''
        if 'confederation peers' in config:
            value = REGEX.search(config).group('value').split()

    elif arg == 'timer_bgp_keepalive':
        REGEX = re.compile(r'(?:timers bgp\s)(?P<value>.*)$', re.M)
        value = ''
        if 'timers bgp' in config:
            parsed = REGEX.search(config).group('value').split()
            value = parsed[0]

    elif arg == 'timer_bgp_hold':
        REGEX = re.compile(r'(?:timers bgp\s)(?P<value>.*)$', re.M)
        value = ''
        if 'timers bgp' in config:
            parsed = REGEX.search(config).group('value').split()
            if len(parsed) == 2:
                value = parsed[1]

    return value


def get_value(arg, config):
    custom = [
        'event_history_cli',
        'event_history_events',
        'event_history_periodic',
        'event_history_detail',
        'confederation_peers',
        'timer_bgp_hold',
        'timer_bgp_keepalive'
    ]

    if arg in BOOL_PARAMS:
        REGEX = re.compile(r'\s+{0}\s*$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = False
        try:
            if REGEX.search(config):
                value = True
        except TypeError:
            value = False
    elif arg in custom:
        value = get_custom_value(config, arg)
    else:
        REGEX = re.compile(r'(?:{0}\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = ''
        if PARAM_TO_COMMAND_KEYMAP[arg] in config:
            value = REGEX.search(config).group('value')
    return value


def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)

    try:
        asn_regex = '.*router\sbgp\s(?P<existing_asn>\d+).*'
        match_asn = re.match(asn_regex, str(netcfg), re.DOTALL)
        existing_asn_group = match_asn.groupdict()
        existing_asn = existing_asn_group['existing_asn']
    except AttributeError:
        existing_asn = ''

    if existing_asn:
        bgp_parent = 'router bgp {0}'.format(existing_asn)
        if module.params['vrf'] != 'default':
            parents = [bgp_parent, 'vrf {0}'.format(module.params['vrf'])]
        else:
            parents = bgp_parent

        config = netcfg.get_section(parents)

        if config:
            # remove the asn
            args.pop(0)

            for arg in args:
                if module.params['vrf'] != 'default':
                    if arg not in GLOBAL_PARAMS:
                        existing[arg] = get_value(arg, config)
                else:
                    existing[arg] = get_value(arg, config)

            existing['asn'] = existing_asn
            if module.params['vrf'] == 'default':
                existing['vrf'] = 'default'

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


def state_present(module, existing, proposed):
    commands = list()
    proposed_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, proposed)
    existing_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, existing)

    for key, value in proposed_commands.iteritems():
        if value is True:
            commands.append(key)
        elif value is False:
            commands.append('no {0}'.format(key))
        elif value == 'default':
            if key == 'vrf':
                pass
            elif key in PARAM_TO_DEFAULT_KEYMAP.keys():
                commands.append('{0} {1}'.format(key, PARAM_TO_DEFAULT_KEYMAP[key]))
            elif existing_commands.get(key):
                existing_value = existing_commands.get(key)
                if key == 'confederation peers':
                    commands.append('no {0} {1}'.format(key, ' '.join(existing_value)))
                else:
                    commands.append('no {0} {1}'.format(key, existing_value))
            else:
                if key.replace(' ', '_').replace('-', '_') in BOOL_PARAMS:
                    commands.append('no {0}'.format(key))
        else:
            if key == 'confederation peers':
                existing_confederation_peers = existing.get('confederation_peers')

                if not isinstance(existing_confederation_peers, list):
                    existing_confederation_peers = [existing_confederation_peers]

                values = value.split()
                for each_value in values:
                    if each_value not in existing_confederation_peers:
                        existing_confederation_peers.append(each_value)
                peer_string = ' '.join(existing_confederation_peers)
                commands.append('{0} {1}'.format(key, peer_string))
            else:
                if value.startswith('size'):
                    value = value.replace('_', ' ')
                command = '{0} {1}'.format(key, value)
                commands.append(command)

    asn_command = 'router bgp {0}'.format(module.params['asn'])
    if asn_command in commands:
        commands.remove(asn_command)
    commands.insert(0, asn_command)
    return commands


def state_absent(module, existing, proposed):
    commands = []
    if module.params['vrf'] == 'default':
        commands.append('no router bgp {0}'.format(module.params['asn']))
    else:
        if existing.get('vrf') == proposed.get('vrf'):
            commands.append('router bgp {0}'.format(module.params['asn']))
            commands.append('no vrf {0}'.format(module.params['vrf']))

    return commands


def fix_commands(commands, module):
    local_as_command = ''
    confederation_id_command = ''

    for command in commands:
        if 'local-as' in command:
            local_as_command = command
        elif 'confederation identifier' in command:
            confederation_id_command = command

    if local_as_command and confederation_id_command:
        commands.pop(commands.index(local_as_command))
        commands.pop(commands.index(confederation_id_command))

        commands.append(local_as_command)
        commands.append(confederation_id_command)

    if module.params['state'] == 'present':
        if module.params['vrf'] != 'default':
            vrf_command = 'vrf {0}'.format(module.params['vrf'])

            if vrf_command not in commands:
                commands.insert(0, vrf_command)

    asn_command = 'router bgp {0}'.format(module.params['asn'])
    if asn_command in commands:
        commands.remove(asn_command)
    commands.insert(0, asn_command)

    return commands


def custom_load_config(module, temp_commands):
    commands = list()
    netcfg = get_config(module)
    bgp_parent = 'router bgp {0}'.format(module.params['asn'])
    if module.params['vrf'] != 'default':
        parents = [bgp_parent, 'vrf {0}'.format(module.params['vrf'])]
    else:
        parents = bgp_parent

    section = netcfg.get_section(parents)
    if section:
        splitted_section = section.splitlines()
        splitted_section.append('router bgp {0}'.format(module.params['asn']))
    else:
        splitted_section = []

    stripped_section = [elem.strip() for elem in splitted_section]
    commands = [command for command in temp_commands if command not in stripped_section]

    save_config = module.params['save_config']
    result = dict(changed=False)

    if commands:
        commands = fix_commands(commands, module)

        if not module.check_mode:
            module.config(commands)
            if save_config:
                module.config.save_config()

        result['changed'] = True
        result['updates'] = commands

    return result


def main():
    argument_spec = dict(
            asn=dict(required=True, type='str'),
            vrf=dict(required=False, type='str', default='default'),
            bestpath_always_compare_med=dict(required=False, choices=ACCEPTED),
            bestpath_aspath_multipath_relax=dict(required=False, choices=ACCEPTED),
            bestpath_compare_neighborid=dict(required=False, choices=ACCEPTED),
            bestpath_compare_routerid=dict(required=False, choices=ACCEPTED),
            bestpath_cost_community_ignore=dict(required=False, choices=ACCEPTED),
            bestpath_med_confed=dict(required=False, choices=ACCEPTED),
            bestpath_med_missing_as_worst=dict(required=False, choices=ACCEPTED),
            bestpath_med_non_deterministic=dict(required=False, choices=ACCEPTED),
            cluster_id=dict(required=False, type='str'),
            confederation_id=dict(required=False, type='str'),
            confederation_peers=dict(required=False, type='str'),
            disable_policy_batching=dict(required=False, choices=ACCEPTED),
            disable_policy_batching_ipv4_prefix_list=dict(required=False, type='str'),
            disable_policy_batching_ipv6_prefix_list=dict(required=False, type='str'),
            enforce_first_as=dict(required=False, choices=ACCEPTED),
            event_history_cli=dict(required=False, choices=['true', 'false', 'default', 'size_small', 'size_medium', 'size_large', 'size_disable']),
            event_history_detail=dict(required=False, choices=['true', 'false', 'default', 'size_small', 'size_medium', 'size_large', 'size_disable']),
            event_history_events=dict(required=False, choices=['true', 'false', 'default' 'size_small', 'size_medium', 'size_large', 'size_disable']),
            event_history_periodic=dict(required=False, choices=['true', 'false', 'default', 'size_small', 'size_medium', 'size_large', 'size_disable']),
            fast_external_fallover=dict(required=False, choices=ACCEPTED),
            flush_routes=dict(required=False, choices=ACCEPTED),
            graceful_restart=dict(required=False, choices=ACCEPTED),
            graceful_restart_helper=dict(required=False, choices=ACCEPTED),
            graceful_restart_timers_restart=dict(required=False, choices=ACCEPTED),
            graceful_restart_timers_stalepath_time=dict(required=False, type='str'),
            isolate=dict(required=False, choices=ACCEPTED),
            local_as=dict(required=False, type='str'),
            log_neighbor_changes=dict(required=False, choices=ACCEPTED),
            maxas_limit=dict(required=False, type='str'),
            neighbor_down_fib_accelerate=dict(required=False, choices=ACCEPTED),
            reconnect_interval=dict(required=False, type='str'),
            router_id=dict(required=False, type='str'),
            shutdown=dict(required=False, choices=ACCEPTED),
            suppress_fib_pending=dict(required=False, choices=ACCEPTED),
            timer_bestpath_limit=dict(required=False, type='str'),
            timer_bgp_hold=dict(required=False, type='str'),
            timer_bgp_keepalive=dict(required=False, type='str'),
            m_facts=dict(required=False, default=False, type='bool'),
            state=dict(choices=['present', 'absent'], default='present',
                       required=False),
    )
    argument_spec.update(nxos_argument_spec)
    module = get_module(argument_spec=argument_spec,
                        required_together=[['timer_bgp_hold',
                                            'timer_bgp_keepalive']],
                        supports_check_mode=True)

    state = module.params['state']
    args =  [
            "asn",
            "bestpath_always_compare_med",
            "bestpath_aspath_multipath_relax",
            "bestpath_compare_neighborid",
            "bestpath_compare_routerid",
            "bestpath_cost_community_ignore",
            "bestpath_med_confed",
            "bestpath_med_missing_as_worst",
            "bestpath_med_non_deterministic",
            "cluster_id",
            "confederation_id",
            "confederation_peers",
            "disable_policy_batching",
            "disable_policy_batching_ipv4_prefix_list",
            "disable_policy_batching_ipv6_prefix_list",
            "enforce_first_as",
            "event_history_cli",
            "event_history_detail",
            "event_history_events",
            "event_history_periodic",
            "fast_external_fallover",
            "flush_routes",
            "graceful_restart",
            "graceful_restart_helper",
            "graceful_restart_timers_restart",
            "graceful_restart_timers_stalepath_time",
            "isolate",
            "local_as",
            "log_neighbor_changes",
            "maxas_limit",
            "neighbor_down_fib_accelerate",
            "reconnect_interval",
            "router_id",
            "shutdown",
            "suppress_fib_pending",
            "timer_bestpath_limit",
            "timer_bgp_hold",
            "timer_bgp_keepalive",
            "vrf"
        ]

    if module.params['vrf'] != 'default':
        for param, inserted_value in module.params.iteritems():
            if param in GLOBAL_PARAMS and inserted_value:
                module.fail_json(msg='Global params can be modifed only'
                                     ' under "default" VRF.',
                                     vrf=module.params['vrf'],
                                     global_param=param)

    existing = invoke('get_existing', module, args)

    if existing.get('asn'):
        if (existing.get('asn') != module.params['asn'] and
            state == 'present'):
            module.fail_json(msg='Another BGP ASN already exists.',
                             proposed_asn=module.params['asn'],
                             existing_asn=existing.get('asn'))

    end_state = existing
    proposed_args = dict((k, v) for k, v in module.params.iteritems()
                    if v is not None and k in args)
    proposed = {}
    for key, value in proposed_args.iteritems():
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.lower() == 'default':
            value = PARAM_TO_DEFAULT_KEYMAP.get(key)
            if value is None:
                if key in BOOL_PARAMS:
                    value = False
                else:
                    value = 'default'
        if existing.get(key) or (not existing.get(key) and value):
            proposed[key] = value

    result = {}
    if state == 'present' or (state == 'absent' and existing):
        temp_commands = invoke('state_%s' % state, module, existing, proposed)

        try:
            response = custom_load_config(module, temp_commands)
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
