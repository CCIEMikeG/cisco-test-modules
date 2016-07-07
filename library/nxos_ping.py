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
module: nxos_ping
version_added: "2.1"
short_description: Tests reachability using ping from Nexus switch
description:
    - Tests reachability using ping from switch to a remote destination
extends_documentation_fragment: nxos
author: Jason Edelman (@jedelman8), Gabriele Gerbino (@GGabriele)
options:
    dest:
        description:
            - IP address or hostname (resolvable by switch) of remote node
        required: true
    count:
        description:
            - Number of packets to send
        required: false
        default: 2
    source:
        description:
            - Source IP Address
        required: false
        default: null
    vrf:
        description:
            - Outgoing VRF
        required: false
        default: null
'''

EXAMPLES = '''
# test reachability to 8.8.8.8 using mgmt vrf
- nxos_ping: dest=8.8.8.8 vrf=management host=68.170.147.165
# Test reachability to a few different public IPs using mgmt vrf
- nxos_ping: dest=nxos_ping vrf=management host=68.170.147.165
  with_items:
    - 8.8.8.8
    - 4.4.4.4
    - 198.6.1.4
'''

RETURN = '''
action:
    description:
        - Show what action has been performed
    returned: always
    type: string
    sample: "PING 8.8.8.8 (8.8.8.8): 56 data bytes"
updates:
    description: Show the command sent
    returned: always
    type: list
    sample: ["ping 8.8.8.8 count 2 vrf management"]
count:
    description: Show amount of packets sent
    returned: always
    type: string
    sample: "2"
dest:
    description: Show the ping destination
    returned: always
    type: string
    sample: "8.8.8.8"
rtt:
    description: Show RTT stats
    returned: always
    type: dict
    sample: {"avg": "6.264","max":"6.564",
            "min": "5.978"}
packets_rx:
    description: Packets successfully received
    returned: always
    type: string
    sample: "2"
packets_tx:
    description: Packets successfully transmitted
    returned: always
    type: string
    sample: "2"
packet_loss:
    description: Percentage of packets lost
    returned: always
    type: string
    sample: "0.00%"
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

def get_summary(results_list, reference_point):
    summary_string = results_list[reference_point+1]
    summary_list = summary_string.split(',')
    pkts_tx = summary_list[0].split('packets')[0].strip()
    pkts_rx = summary_list[1].split('packets')[0].strip()
    pkt_loss = summary_list[2].split('packet')[0].strip()
    summary = dict(packets_tx=pkts_tx,
                   packets_rx=pkts_rx,
                   packet_loss=pkt_loss)

    if 'bytes from' not in results_list[reference_point-2]:
        ping_pass = False
    else:
        ping_pass = True

    return summary, ping_pass


def get_rtt(results_list, packet_loss, location):
    if packet_loss != '100.00%':
        rtt_string = results_list[location]
        base = rtt_string.split('=')[1]
        rtt_list = base.split('/')
        min_rtt = rtt_list[0].lstrip()
        avg_rtt = rtt_list[1]
        max_rtt = rtt_list[2][:-3]
        rtt = dict(min=min_rtt, avg=avg_rtt, max=max_rtt)
    else:
        rtt = dict(min=None, avg=None, max=None)

    return rtt


def get_statistics_summary_line(response_as_list):
    for each in response_as_list:
        if '---' in each:
            index = response_as_list.index(each)
    return index


def execute_show(cmds, module, command_type=None):
    try:
        if command_type:
            response = module.execute(cmds, command_type=command_type)
        else:
            response = module.execute(cmds)
    except ShellError:
        clie = get_exception()
        module.fail_json(msg='Error sending {0}'.format(cmds),
                         error=str(clie))
    return response


def execute_show_command_ping(command, module, command_type='cli_show_ascii'):
    cmds = [command]
    if module.params['transport'] == 'cli':
        body = execute_show(cmds, module)
    elif module.params['transport'] == 'nxapi':
        body = execute_show(cmds, module, command_type=command_type)
    return body


def get_ping_results(command, module, transport):
    ping = execute_show_command_ping(command, module)[0]

    if not ping:
        module.fail_json(msg="An unexpected error occurred. Check all params.",
                         command=command, destination=module.params['dest'],
                         vrf=module.params['vrf'],
                         source=module.params['source'])

    elif "can't bind to address" in ping:
        module.fail_json(msg="Can't bind to source address.", command=command)
    elif "bad context" in ping:
        module.fail_json(msg="Wrong VRF name inserted.", command=command,
                         vrf=module.params['vrf'])
    else:
        splitted_ping = ping.split('\n')
        reference_point = get_statistics_summary_line(splitted_ping)
        summary, ping_pass = get_summary(splitted_ping, reference_point)
        rtt = get_rtt(splitted_ping, summary['packet_loss'], reference_point+2)

    return (splitted_ping, summary, rtt, ping_pass)


def main():
    argument_spec = dict(
            dest=dict(required=True),
            count=dict(required=False, default=2),
            vrf=dict(required=False),
            source=dict(required=False),
            state=dict(required=False, choices=['present', 'absent'],
                       default='present'),
    )
    module = get_module(argument_spec=argument_spec,
                        supports_check_mode=True)

    destination = module.params['dest']
    count = module.params['count']
    vrf = module.params['vrf']
    source = module.params['source']
    state = module.params['state']

    if count:
        try:
            if int(count) < 1 or int(count) > 655350:
                raise ValueError
        except ValueError:
            module.fail_json(msg="'count' must be an integer between 1 "
                                 "and 655350.", count=count)

    OPTIONS = {
        'vrf': vrf,
        'count': count,
        'source': source
        }

    ping_command = 'ping {0}'.format(destination)
    for command, arg in OPTIONS.iteritems():
        if arg:
            ping_command += ' {0} {1}'.format(command, arg)

    ping_results, summary, rtt, ping_pass = get_ping_results(
                    ping_command, module, module.params['transport'])

    packet_loss = summary['packet_loss']
    packets_rx = summary['packets_rx']
    packets_tx = summary['packets_tx']

    results = {}
    results['updates'] = [ping_command]
    results['action'] = ping_results[1]
    results['dest'] = destination
    results['count'] = count
    results['packets_tx'] = packets_tx
    results['packets_rx'] = packets_rx
    results['packet_loss'] = packet_loss
    results['rtt'] = rtt
    results['state'] = module.params['state']

    if ping_pass and state == 'absent':
        module.fail_json(msg="Ping succeeded unexpectedly", results=results)
    elif not ping_pass and state == 'present':
        module.fail_json(msg="Ping failed unexpectedly", results=results)
    else:
        module.exit_json(**results)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from ansible.module_utils.nxos import *
if __name__ == '__main__':
    main()
