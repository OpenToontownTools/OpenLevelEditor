from . import AnimatedProp
from direct.actor import Actor
from direct.interval.IntervalGlobal import *

class HalloweenBloodsuckerAnimatedProp(AnimatedProp.AnimatedProp):

    def __init__(self, node):
        AnimatedProp.AnimatedProp.__init__(self, node)
        parent = node.getParent()
        self.tube = Actor.Actor(node, copy=0)
        self.tube.reparentTo(parent)
        self.tube.loadAnims({'wave': 'tt_a_ara_pty_tubeCogVictory_wave'})
        self.tube.pose('wave', 0)
        self.tube.setBlend(frameBlend=base.settings.getBool("game", "smooth-animations", True))
        self.node = self.tube

    def delete(self):
        AnimatedProp.AnimatedProp.delete(self)
        self.tube.cleanup()
        del self.tube
        del self.node

    def enter(self):
        AnimatedProp.AnimatedProp.enter(self)
        self.tube.setPlayRate(0.7, 'wave')
        self.tube.loop('wave')

    def exit(self):
        AnimatedProp.AnimatedProp.exit(self)
        self.tube.stop()
