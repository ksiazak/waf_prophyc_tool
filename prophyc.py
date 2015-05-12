#!/usr/bin/env python
# encoding: utf-8
# Mateusz Piorko, 2015
# Nokia Networks

"""

Example::

    def configure(conf):
        conf.load(prophyc)

    def build(bld):
        bld(
            features='prophyc cxx',
            input_mode='isar',
            output_mode='cpp_full_out',
            patch='test.patch',
            source='test.hpp',
            install_path='/tmp/',
            target='prohyc_test)

        bld.prophyc(
            features='cxx',
            input_mode='isar',
            output_mode='cpp_full_out',
            patch='test.patch',
            source='test.hpp',
            install_path='/tmp/',
            target='prohyc_test)
"""

import os
from waflib.Task import Task
from waflib.TaskGen import feature, extension
from waflib.Configure import conf
from waflib.Node import Node
from waflib import Utils
from waflib.Tools.ccroot import USELIB_VARS

USELIB_VARS['prophyc'] = set(['INCLUDES'])

class prophyc(Task):
    run_str = '${PROPHYC} ${PROPHYC_INPUT_MODE} ${PROPHYC_PATCH} ${PROPHYC_PATCH_FILE} ${PROPHYC_ST:INCPATHS} ${PROPHYC_OUTPUT_MODE} ${TGT[0].parent.abspath()} ${SRC[0].abspath()}'
    color = 'BLUE'

prophyc_input_modes = [
    'prophy',
    'isar',
    'sack',
]

prophyc_output_modes = [
    'python_out',
    'cpp_out',
    'cpp_full_out',
]

class WrongProphyInputModeException(Exception):
    def __init__(self, input_mode):
        print('Wrong prophy input mode provided (\'' + input_mode + '\'). ' +
              'Please provide one of following: ' + ', '.join(prophyc_input_modes))

class WrongProphyOutputModeException(Exception):
    def __init__(self, output_mode):
        print('Wrong prophy output mode provided (\'' + output_mode + '\'). ' +
              'Please provide one of following: ' + ', '.join(prophyc_output_modes))

class MissingProphycModeException(Exception):
    def __init__(self):
        print('Missing prophyc input/output mode')

@feature('prophyc')
def use_prophyc(self):
    if not (hasattr(self, 'input_mode') and hasattr(self, 'output_mode')):
        raise(MissingProphycModeException)
    if self.input_mode not in prophyc_input_modes:
        raise(WrongProphyInputModeException(self.input_mode))
    if self.output_mode not in prophyc_output_modes:
        raise(WrongProphyOutputModeException(self.output_mode))
    self.process_use()
    self.propagate_uselib_vars()
    self.apply_incpaths()

    if self.input_mode != 'prophy':
        self.env.PROPHYC_INPUT_MODE = '--' + self.input_mode
    self.env.PROPHYC_OUTPUT_MODE = '--' + self.output_mode
    if hasattr(self, 'patch'):
        self.env.PROPHYC_PATCH = '--patch'
        self.env.PROPHYC_PATCH_FILE = self.to_nodes(self.patch)[0].abspath()

@extension('.prophy', '.h', '.hpp', '.xml')
def process_prophyc(self, node):
    if not hasattr(self, 'output_mode'):
        raise(MissingProphycModeException)
    if self.output_mode == 'python_out':
        out_nodes = [node.change_ext('.py')]
    elif self.output_mode == 'cpp_out':
        compile_node = node.change_ext('.pp.cpp')
        out_nodes = [compile_node, node.change_ext('.pp.hpp')]
    elif self.output_mode == 'cpp_full_out':
        compile_node = node.change_ext('.ppf.cpp')
        out_nodes = [compile_node, node.change_ext('.ppf.hpp')]
    tsk = self.create_task('prophyc', node, out_nodes)
    if hasattr(self, 'install_path'):
        self.bld.install_files(self.install_path, tsk.outputs[:], env=self.env)
    if len(filter(lambda feature: feature in self.features, ['c', 'cxx'])):
        self.source.append(compile_node)

def configure(conf):
    conf.find_program('prophyc', var='PROPHYC')
    conf.env.PROPHYC_ST = '-I%s'

@conf
def prophyc(bld, *k, **kw):
    try:
        kw['features'] += ' prophyc'
    except(KeyError):
        kw['features'] = 'prophyc'
    return bld(*k, **kw)
