#!/usr/bin/env python2
import builtins

builtins.process = 'client'


builtins.__dict__.update(__import__('panda3d.core', fromlist = ['*']).__dict__)
builtins.__dict__.update(__import__('libotp', fromlist = ['*']).__dict__)
builtins.__dict__.update(__import__('libtoontown', fromlist = ['*']).__dict__)
from direct.directbase.DirectStart import *
loadPrcFileData('', 'model-path ../../')
loadPrcFileData('', 'notify-level info')
loadPrcFileData('', 'default-model-extension .bam')
from . import LevelEditor
#base.le = LevelEditor.LevelEditor()
# [gjeon] Don't use this yet
# to start leveleditor use
# from toontown.leveleditor import LevelEditor
