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
module: nxos_bgp_neighbor
version_added: "2.1"
short_description: Manages BGP neighbors configurations
description:
    - Manages BGP neighbors configurations on NX-OS switches
author: Gabriele Gerbino (@GGabriele)
extends_documentation_fragment: nxos
notes:
    - State 'absent' removes the whole BGP neighbor configuration
    - 'default' restores params default value
options:
    asn:
        description:
            - BGP autonomous system number. Valid values are String,
              Integer in ASPLAIN or ASDOT notation.
        required: true
    vrf:
        description:
            - Name of the VRF. The name 'default' is a valid VRF representing
              the global bgp.
        required: false
        default: default
    neighbor:
        description:
            - Neighbor Identifier. Valid values are string. Neighbors may use
              IPv4 or IPv6 notation, with or without prefix length.
        required: true
    description:
        description:
            - Description of the neighbor.
        required: false
        default: null
    connected_check:
        description:
            - Configure whether or not to check for directly connected peer.
        required: false
        choices: ['true', 'false']
        default: null
    capability_negotiation:
        description:
            - Configure whether or not to negotiate capability with
              this neighbor.
        required: false
        choices: ['true', 'false']
        default: null
    dynamic_capability:
        description:
            - Configure whether or not to enable dynamic capability.
        required: false
        choices: ['true', 'false']
        default: null
    ebgp_multihop:
        description:
            - Specify multihop TTL for a remote peer. Valid values are
              integers between 2 and 255, or keyword 'default' to disable
              this property.
        required: false
        default: null
    local_as:
        description:
            - Specify the local-as number for the eBGP neighbor.
              Valid values are String or Integer in ASPLAIN or ASDOT notation,
              or 'default', which means not to configure it.
        required: false
        default: null
    log_neighbor_changes:
        description:
            - Specify whether or not to enable log messages for neighbor
             up/down event.
        required: false
        choices: ['enable', 'disable']
        default: null
    low_memory_exempt:
        description:
            - Specify whether or not to shut down this neighbor under
              memory pressure.
        required: false
        choices: ['true', 'false', 'default']
        default: null
    maximum_peers:
        description:
            - Specify Maximum number of peers for this neighbor prefix
              Valid values are between 1 and 1000, or 'default', which does
              not impose the limit.
        required: false
        default: null
    pwd:
        description:
            - Specify the password for neighbor. Valid value is string.
        required: false
        default: null
    pwd_type:
        description:
            - Specify the encryption type the password will use. Valid values
              are 'cleartext', '3des' or 'cisco_type_7' encryption, and
              'default', which defaults to 'cleartext'.
        required: false
        choices: ['cleartext', '3des', 'cisco_type_7', 'default']
        default: null
    remote_as:
        description:
            - Specify Autonomous System Number of the neighbor.
              Valid values are String or Integer in ASPLAIN or ASDOT notation,
              or 'default', which means not to configure it.
        required: false
        default: null
    remove_private_as:
        description:
            - Specify the config to remove private AS number from outbound
              updates. Valid values are 'enable' to enable this config,
              'disable' to disable this config, 'all' to remove all
              private AS number, or 'replace-as', to replace the private
              AS number.
        required: false
        choices: ['enable', 'disable', 'all', 'replace-as']
        default: null
    shutdown:
        description:
            - Configure to administratively shutdown this neighbor.
        required: false
        choices: ['true','false']
        default: null
    suppress_4_byte_as:
        description:
            - Configure to suppress 4-byte AS Capability.
        required: false
        choices: ['true','false', 'default']
        default: null
    timers_keepalive:
        description:
            - Specify keepalive timer value. Valid values are integers
              between 0 and 3600 in terms of seconds, or 'default',
              which is 60.
        required: false
        default: null
    timers_holdtime:
        description:
            - Specify holdtime timer value. Valid values are integers between
              0 and 3600 in terms of seconds, or 'default', which is 180.
        required: false
        default: null
    transport_passive_only:
        description:
            - Specify whether or not to only allow passive connection setup.
              Valid values are 'true', 'false', and 'default', which defaults
              to 'false'. This property can only be configured when the
              neighbor is in 'ip' address format without prefix length.
              This property and the transport_passive_mode property are
              mutually exclusive.
        required: false
        choices: ['true','false', 'default']
        default: null
    update_source:
        description:
            - Specify source interface of BGP session and updates.
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
# create a new neighbor
- nxos_bgp_neighbor:
    asn: 65535
    neighbor: 3.3.3.3
    local_as: 20
    remote_as: 30
    description: "just a description"
    update_source: Ethernet1/3
    shutdown: default
    state: present
'''

# COMMON CODE FOR MIGRATION

import re
import time
import collections
import itertools
import shlex
import itertools

from ansible.module_utils.basic import BOOLEANS_TRUE, BOOLEANS_FALSE

DEFAULT_COMMENT_TOKENS = ['#', '!']

class ConfigLine(object):

    def __init__(self, text):
        self.text = text
        self.children = list()
        self.parents = list()
        self.raw = None

    @property
    def line(self):
        line = ['set']
        line.extend([p.text for p in self.parents])
        line.append(self.text)
        return ' '.join(line)

    def __str__(self):
        return self.raw

    def __eq__(self, other):
        if self.text == other.text:
            return self.parents == other.parents

    def __ne__(self, other):
        return not self.__eq__(other)

def ignore_line(text, tokens=None):
    for item in (tokens or DEFAULT_COMMENT_TOKENS):
        if text.startswith(item):
            return True

def get_next(iterable):
    item, next_item = itertools.tee(iterable, 2)
    next_item = itertools.islice(next_item, 1, None)
    return itertools.izip_longest(item, next_item)

def parse(lines, indent, comment_tokens=None):
    toplevel = re.compile(r'\S')
    childline = re.compile(r'^\s*(.+)$')

    ancestors = list()
    config = list()

    for line in str(lines).split('\n'):
        text = str(re.sub(r'([{};])', '', line)).strip()

        cfg = ConfigLine(text)
        cfg.raw = line

        if not text or ignore_line(text, comment_tokens):
            continue

        # handle top level commands
        if toplevel.match(line):
            ancestors = [cfg]

        # handle sub level commands
        else:
            match = childline.match(line)
            line_indent = match.start(1)
            level = int(line_indent / indent)
            parent_level = level - 1

            cfg.parents = ancestors[:level]

            if level > len(ancestors):
                config.append(cfg)
                continue

            for i in range(level, len(ancestors)):
                ancestors.pop()

            ancestors.append(cfg)
            ancestors[parent_level].children.append(cfg)

        config.append(cfg)

    return config


class CustomNetworkConfig(object):

    def __init__(self, indent=None, contents=None, device_os=None):
        self.indent = indent or 1
        self._config = list()
        self._device_os = device_os

        if contents:
            self.load(contents)

    @property
    def items(self):
        return self._config

    @property
    def lines(self):
        lines = list()
        for item, next_item in get_next(self.items):
            if next_item is None:
                lines.append(item.line)
            elif not next_item.line.startswith(item.line):
                lines.append(item.line)
        return lines

    def __str__(self):
        text = ''
        for item in self.items:
            if not item.parents:
                expand = self.get_section(item.text)
                text += '%s\n' % self.get_section(item.text)
        return str(text).strip()

    def load(self, contents):
        self._config = parse(contents, indent=self.indent)

    def load_from_file(self, filename):
        self.load(open(filename).read())

    def get(self, path):
        if isinstance(path, basestring):
            path = [path]
        for item in self._config:
            if item.text == path[-1]:
                parents = [p.text for p in item.parents]
                if parents == path[:-1]:
                    return item

    def search(self, regexp, path=None):
        regex = re.compile(r'^%s' % regexp, re.M)

        if path:
            parent = self.get(path)
            if not parent or not parent.children:
                return
            children = [c.text for c in parent.children]
            data = '\n'.join(children)
        else:
            data = str(self)

        match = regex.search(data)
        if match:
            if match.groups():
                values = match.groupdict().values()
                groups = list(set(match.groups()).difference(values))
                return (groups, match.groupdict())
            else:
                return match.group()

    def findall(self, regexp):
        regexp = r'%s' % regexp
        return re.findall(regexp, str(self))

    def expand(self, obj, items):
        block = [item.raw for item in obj.parents]
        block.append(obj.raw)

        current_level = items
        for b in block:
            if b not in current_level:
                current_level[b] = collections.OrderedDict()
            current_level = current_level[b]
        for c in obj.children:
            if c.raw not in current_level:
                current_level[c.raw] = collections.OrderedDict()

    def to_lines(self, section):
        lines = list()
        for entry in section[1:]:
            line = ['set']
            line.extend([p.text for p in entry.parents])
            line.append(entry.text)
            lines.append(' '.join(line))
        return lines

    def to_block(self, section):
        return '\n'.join([item.raw for item in section])

    def get_section(self, path):
        try:
            section = self.get_section_objects(path)
            if self._device_os == 'junos':
                return self.to_lines(section)
            return self.to_block(section)
        except ValueError:
            return list()

    def get_section_objects(self, path):
        if not isinstance(path, list):
            path = [path]
        obj = self.get_object(path)
        if not obj:
            raise ValueError('path does not exist in config')
        return self.expand_section(obj)

    def expand_section(self, configobj, S=None):
        if S is None:
            S = list()
        S.append(configobj)
        for child in configobj.children:
            if child in S:
                continue
            self.expand_section(child, S)
        return S

    def flatten(self, data, obj=None):
        if obj is None:
            obj = list()
        for k, v in data.items():
            obj.append(k)
            self.flatten(v, obj)
        return obj

    def get_object(self, path):
        for item in self.items:
            if item.text == path[-1]:
                parents = [p.text for p in item.parents]
                if parents == path[:-1]:
                    return item

    def get_children(self, path):
        obj = self.get_object(path)
        if obj:
            return obj.children

    def difference(self, other, path=None, match='line', replace='line'):
        updates = list()

        config = self.items
        if path:
            config = self.get_children(path) or list()

        if match == 'line':
            for item in config:
                if item not in other.items:
                    updates.append(item)

        elif match == 'strict':
            if path:
                current = other.get_children(path) or list()
            else:
                current = other.items

            for index, item in enumerate(config):
                try:
                    if item != current[index]:
                        updates.append(item)
                except IndexError:
                    updates.append(item)

        elif match == 'exact':
            if path:
                current = other.get_children(path) or list()
            else:
                current = other.items

            if len(current) != len(config):
                updates.extend(config)
            else:
                for ours, theirs in itertools.izip(config, current):
                    if ours != theirs:
                        updates.extend(config)
                        break

        if self._device_os == 'junos':
            return updates

        diffs = collections.OrderedDict()
        for update in updates:
            if replace == 'block' and update.parents:
                update = update.parents[-1]
            self.expand(update, diffs)

        return self.flatten(diffs)

    def replace(self, replace, text=None, regex=None, parents=None,
            add_if_missing=False, ignore_whitespace=False):
        match = None

        parents = parents or list()
        if text is None and regex is None:
            raise ValueError('missing required arguments')

        if not regex:
            regex = ['^%s$' % text]

        patterns = [re.compile(r, re.I) for r in to_list(regex)]

        for item in self.items:
            for regexp in patterns:
                string = item.text if ignore_whitespace is True else item.raw
                if regexp.search(item.text):
                    if item.text != replace:
                        if parents == [p.text for p in item.parents]:
                            match = item
                            break

        if match:
            match.text = replace
            indent = len(match.raw) - len(match.raw.lstrip())
            match.raw = replace.rjust(len(replace) + indent)

        elif add_if_missing:
            self.add(replace, parents=parents)


    def add(self, lines, parents=None):
        """Adds one or lines of configuration
        """

        ancestors = list()
        offset = 0
        obj = None

        ## global config command
        if not parents:
            for line in to_list(lines):
                item = ConfigLine(line)
                item.raw = line
                if item not in self.items:
                    self.items.append(item)

        else:
            for index, p in enumerate(parents):
                try:
                    i = index + 1
                    obj = self.get_section_objects(parents[:i])[0]
                    ancestors.append(obj)

                except ValueError:
                    # add parent to config
                    offset = index * self.indent
                    obj = ConfigLine(p)
                    obj.raw = p.rjust(len(p) + offset)
                    if ancestors:
                        obj.parents = list(ancestors)
                        ancestors[-1].children.append(obj)
                    self.items.append(obj)
                    ancestors.append(obj)

            # add child objects
            for line in to_list(lines):
                # check if child already exists
                for child in ancestors[-1].children:
                    if child.text == line:
                        break
                else:
                    offset = len(parents) * self.indent
                    item = ConfigLine(line)
                    item.raw = line.rjust(len(line) + offset)
                    item.parents = ancestors
                    ancestors[-1].children.append(item)
                    self.items.append(item)


def argument_spec():
    return dict(
        # config options
        running_config=dict(aliases=['config']),
        save_config=dict(type='bool', default=False, aliases=['save'])
    )
nxos_argument_spec = argument_spec()

def get_config(module):
    config = module.params['running_config']
    if not config:
        config = module.get_config()
    return CustomNetworkConfig(indent=2, contents=config)

def load_config(module, candidate):
    config = get_config(module)

    commands = candidate.difference(config)
    commands = [str(c).strip() for c in commands]

    save_config = module.params['save_config']

    result = dict(changed=False)

    if commands:
        if not module.check_mode:
            module.configure(commands)
            if save_config:
                module.config.save_config()

        result['changed'] = True
        result['updates'] = commands

    return result
# END OF COMMON CODE
BOOLEANS_TRUE = ['yes', 'on', '1', 'true', 'True', 1, True]
BOOLEANS_FALSE = ['no', 'off', '0', 'false', 'False', 0, False]
BOOLEANS = BOOLEANS_TRUE + BOOLEANS_FALSE
ACCEPTED = BOOLEANS_TRUE + BOOLEANS_FALSE + ['default']
WARNINGS = []
BOOL_PARAMS = [
    'capability_negotiation',
    'shutdown',
    'connected_check',
    'dynamic_capability',
    'low_memory_exempt',
    'suppress_4_byte_as',
    'transport_passive_only'
]
PARAM_TO_COMMAND_KEYMAP = {
    'asn': 'router bgp',
    'capability_negotiation': 'dont-capability-negotiate',
    'connected_check': 'disable-connected-check',
    'description': 'description',
    'dynamic_capability': 'dynamic-capability',
    'ebgp_multihop': 'ebgp-multihop',
    'local_as': 'local-as',
    'log_neighbor_changes': 'log-neighbor-changes',
    'low_memory_exempt': 'low-memory exempt',
    'maximum_peers': 'maximum-peers',
    'neighbor': 'neighbor',
    'pwd': 'password',
    'pwd_type': 'password-type',
    'remote_as': 'remote-as',
    'remove_private_as': 'remove-private-as',
    'shutdown': 'shutdown',
    'suppress_4_byte_as': 'capability suppress 4-byte-as',
    'timers_keepalive': 'timers-keepalive',
    'timers_holdtime': 'timers-holdtime',
    'transport_passive_only': 'transport connection-mode passive',
    'update_source': 'update-source',
    'vrf': 'vrf'
}
PARAM_TO_DEFAULT_KEYMAP = {
    'shutdown': False,
    'dynamic_capability': True,
    'timers_keepalive': 60,
    'timers_holdtime': 180
}

def invoke(name, *args, **kwargs):
    func = globals().get(name)
    if func:
        return func(*args, **kwargs)


def get_value(arg, config, module):
    if arg in BOOL_PARAMS:
        REGEX = re.compile(r'\s+{0}\s*$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = False
        try:
            if REGEX.search(config):
                value = True
        except TypeError:
            value = False

    else:
        REGEX = re.compile(r'(?:{0}\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = ''
        if PARAM_TO_COMMAND_KEYMAP[arg] in config:
            value = REGEX.search(config).group('value')
    return value


def get_custom_value(arg, config, module):
    value = ''
    splitted_config = config.splitlines()

    if arg == 'log_neighbor_changes':
        for line in splitted_config:
            if 'log-neighbor-changes' in line:
                if 'disable' in line:
                    value = 'disable'
                else:
                    value = 'enable'

    elif arg == 'pwd':
        for line in splitted_config:
            if 'password' in line:
                splitted_line = line.split()
                value = splitted_line[2]

    elif arg == 'pwd_type':
        for line in splitted_config:
            if 'password' in line:
                splitted_line = line.split()
                value = splitted_line[1]

    elif arg == 'remove_private_as':
        value = 'disable'
        for line in splitted_config:
            if 'remove-private-as' in line:
                splitted_line = line.split()
                if len(splitted_line) == 1:
                    value = 'enable'
                elif len(splitted_line) == 2:
                    value = splitted_line[1]

    elif arg == 'timers_keepalive':
        REGEX = re.compile(r'(?:timers\s)(?P<value>.*)$', re.M)
        value = ''
        if 'timers' in config:
            parsed = REGEX.search(config).group('value').split()
            value = parsed[0]

    elif arg == 'timers_holdtime':
        REGEX = re.compile(r'(?:timers\s)(?P<value>.*)$', re.M)
        value = ''
        if 'timers' in config:
            parsed = REGEX.search(config).group('value').split()
            if len(parsed) == 2:
                value = parsed[1]

    return value


def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)
    custom = [
        'log_neighbor_changes',
        'pwd',
        'pwd_type',
        'remove_private_as',
        'timers_holdtime',
        'timers_keepalive'
    ]
    try:
        asn_regex = '.*router\sbgp\s(?P<existing_asn>\d+).*'
        match_asn = re.match(asn_regex, str(netcfg), re.DOTALL)
        existing_asn_group = match_asn.groupdict()
        existing_asn = existing_asn_group['existing_asn']
    except AttributeError:
        existing_asn = ''

    if existing_asn:
        parents = ["router bgp {0}".format(existing_asn)]
        if module.params['vrf'] != 'default':
            parents.append('vrf {0}'.format(module.params['vrf']))

        parents.append('neighbor {0}'.format(module.params['neighbor']))
        config = netcfg.get_section(parents)

        if config:
            for arg in args:
                if arg not in ['asn', 'vrf', 'neighbor']:
                    if arg in custom:
                        existing[arg] = get_custom_value(arg, config, module)
                    else:
                        existing[arg] = get_value(arg, config, module)

            existing['asn'] = existing_asn
            existing['neighbor'] = module.params['neighbor']
            existing['vrf'] = module.params['vrf']
    else:
        WARNINGS.append("The BGP process didn't exist but the task"
                        " just created it.")
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
                if key.replace(' ', '_').replace('-', '_') in BOOL_PARAMS:
                    commands.append('no {0}'.format(key))
        else:
            if key == 'log-neighbor-changes':
                if value == 'enable':
                    command = '{0}'.format(key)
                else:
                    command = '{0} {1}'.format(key, value)
            elif key == 'password':
                pwd_type = module.params['pwd_type']
                if pwd_type == '3des':
                    pwd_type = 3
                else:
                    pwd_type = 7
                command = '{0} {1} {2}'.format(key, pwd_type, value)
                if command not in commands:
                    commands.append(command)
            elif key == 'remove-private-as':
                if value == 'enable':
                    command = '{0}'.format(key)
                    commands.append(command)
                elif value == 'disable':
                    if existing_commands.get(key) != 'disable':
                        command = 'no {0}'.format(key)
                        commands.append(command)
                else:
                    command = '{0} {1}'.format(key, value)
                    commands.append(command)
            elif key.startswith('timers'):
                command = 'timers {0} {1}'.format(
                    proposed_commands['timers-keepalive'],
                    proposed_commands['timers-holdtime'])
                if command not in commands:
                    commands.append(command)
            else:
                command = '{0} {1}'.format(key, value)
                commands.append(command)

    if commands:
        parents = ["router bgp {0}".format(module.params['asn'])]
        if module.params['vrf'] != 'default':
            parents.append('vrf {0}'.format(module.params['vrf']))

        parents.append('neighbor {0}'.format(module.params['neighbor']))

        # make sure that local-as is the last command in the list.
        local_as_command = 'local-as {0}'.format(module.params['local_as'])
        if local_as_command in commands:
            commands.remove(local_as_command)
            commands.append(local_as_command)
        candidate.add(commands, parents=parents)


def state_absent(module, existing, proposed, candidate):
    commands = []
    parents = ["router bgp {0}".format(module.params['asn'])]
    if module.params['vrf'] != 'default':
        parents.append('vrf {0}'.format(module.params['vrf']))

    commands.append('no neighbor {0}'.format(module.params['neighbor']))
    candidate.add(commands, parents=parents)


def main():
    argument_spec = dict(
            asn=dict(required=True, type='str'),
            vrf=dict(required=False, type='str', default='default'),
            neighbor=dict(required=True, type='str'),
            description=dict(required=False, type='str'),
            capability_negotiation=dict(required=False, type='bool', choices=BOOLEANS),
            connected_check=dict(required=False, type='bool', choices=BOOLEANS),
            dynamic_capability=dict(required=False, type='str', choices=ACCEPTED),
            ebgp_multihop=dict(required=False, type='str'),
            local_as=dict(required=False, type='str'),
            log_neighbor_changes=dict(required=False, type='str', choices=['enable', 'disable']),
            low_memory_exempt=dict(required=False, type='str', choices=ACCEPTED),
            maximum_peers=dict(required=False, type='str'),
            pwd=dict(required=False, type='str'),
            pwd_type=dict(required=False, type='str', choices=['cleartext', '3des', 'cisco_type_7', 'default']),
            remote_as=dict(required=False, type='str'),
            remove_private_as=dict(required=False, type='str', choices=['enable', 'disable', 'all', 'replace-as']),
            shutdown=dict(required=False, type='str'),
            suppress_4_byte_as=dict(required=False, type='str', choices=ACCEPTED),
            timers_keepalive=dict(required=False, type='str'),
            timers_holdtime=dict(required=False, type='str'),
            transport_passive_only=dict(required=False, type='str', choices=ACCEPTED),
            update_source=dict(required=False, type='str'),
            m_facts=dict(required=False, default=False, type='bool'),
            state=dict(choices=['present', 'absent'], default='present',
                       required=False),
            include_defaults=dict(default=True)
    )
    argument_spec.update(nxos_argument_spec)
    module = get_module(argument_spec=argument_spec,
                        required_together=[['pwd', 'pwd_type']],
                        supports_check_mode=True)

    state = module.params['state']
    if module.params['pwd_type'] == 'default':
        module.params['pwd_type'] = '0'

    args =  [
            'asn',
            'capability_negotiation',
            'connected_check',
            'description',
            'dynamic_capability',
            'ebgp_multihop',
            'local_as',
            'log_neighbor_changes',
            'low_memory_exempt',
            'maximum_peers',
            'neighbor',
            'pwd',
            'pwd_type',
            'remote_as',
            'remove_private_as',
            'shutdown',
            'suppress_4_byte_as',
            'timers_keepalive',
            'timers_holdtime',
            'transport_passive_only',
            'update_source',
            'vrf'
        ]

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
        if key not in ['asn', 'vrf', 'neighbor', 'pwd_type']:
            if str(value).lower() == 'true':
                value = True
            elif str(value).lower() == 'false':
                value = False
            elif str(value).lower() == 'default':
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
        candidate = CustomNetworkConfig(indent=3)
        invoke('state_%s' % state, module, existing, proposed, candidate)

        try:
            response = load_config(module, candidate)
            result.update(response)
        except ShellError:
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

    if WARNINGS:
        result['warnings'] = WARNINGS

    module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from ansible.module_utils.nxos import *
if __name__ == '__main__':
    main()
