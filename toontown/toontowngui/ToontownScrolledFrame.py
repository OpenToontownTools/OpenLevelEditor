"""
Toontown Realms Scrolled Frame:
Wrapper for DirectScrolledFrame - but it auto sizes and places the elements and gets rid of the hassle of using it

item1 = OnscreenText('This is a text object'...)
item2 = AnimatedButton('Animated!!!', command = xxx...)
frame = ToontownScrolledFrame(
                        parent = x,
                        pos = Vec3(x,x,x),
                        width = ##,
                        height = ##)
frame.addItems(item1, item2, ...)

"""
from typing import Union, Tuple, Dict, Optional, List

from direct.gui import DirectGuiGlobals
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectGuiBase import DirectGuiBase, DirectGuiWidget
from panda3d.core import NodePath


class ToontownScrolledFrame(DirectScrolledFrame):

    def __init__(self, parent, **kwargs):
        optiondefs = (
            ('relief', None, None),
            ('state', DirectGuiGlobals.NORMAL, None),
            ('manageScrollBars', False, None),
            ('scrollBarWidth', 0.05, None),
            ('autoHideScrollBars', True, None),
            ('verticalScroll_relief', None, None),
            ('width', 1.0, None),
            ('height', 1.0, None),
            ('itemPadding', 0.05, None),
            ('itemMargin', (0, 0), None),
            # If we have this, we can auto determine the z padding (we still will add itemPadding tho)
            ('useItemBoundsForPadding', False, None)
        )
        self.defineoptions(kwargs, optiondefs)
        super().__init__(parent, **kwargs)
        self.initialiseoptions(ToontownScrolledFrame)
        self['frameSize'] = (-self['width'], self['width'], -self['height'], self['height'])
        self['canvasSize'] = (-self['width'] + 0.05, self['width'] - 0.05, -self['height']+0.025, self['height'] - 0.025)

        self.verticalScroll.incButton.destroy()
        self.verticalScroll.decButton.destroy()
        self.horizontalScroll.incButton.destroy()
        self.horizontalScroll.decButton.destroy()

        self.items: List[Union[DirectGuiWidget, Tuple[DirectGuiWidget, Optional[Dict[str, float]]]]] = []

    def __scrollUp(self, task = None):
        # We don't gotta do anything if theres nothing to scroll
        if self.verticalScroll.isHidden():
            return

        if self.verticalScroll['value'] > 0:
            self.verticalScroll['value'] -= 1/len(self.items)

    def __scrollDown(self, task = None):
        # We don't gotta do anything if theres nothing to scroll
        if self.verticalScroll.isHidden():
            return

        if self.verticalScroll['value'] < 1.0:
            self.verticalScroll['value'] += 1/len(self.items)

    def destroy(self):
        for item in self.items:
            item[0].destroy()

        del self.items[:]
        super().destroy()

    def clearItems(self):
        """
        Clears all items in the frame
        """
        for item in self.items:
            item[0].destroy()

        del self.items[:]
        self.items = []

    def removeItem(self, item: Union[DirectGuiWidget, Tuple[DirectGuiWidget, Optional[Dict[str, float]]]]):
        """
        Removes an item from the frame.
        """
        if isinstance(item, tuple):
            if item in self.items:
                item[0].destroy()
                self.items.remove(item)
        else:
            for i in self.items:
                if item == i[0]:
                    item.destroy()
                    self.items.remove(i)

        self.buildFrame()

    def insertItems(self, *items: Union[DirectGuiWidget, Tuple[DirectGuiWidget, Optional[Dict[str, float]]]], index: int = 0):
        """
        Add items to the scrolled list, then we auto arrange them

        :param items: All items
        :param index: Position where all items should go.
        """
        for item in items:
            if isinstance(item, tuple):
                # If it's a tuple, we have added some sort of offset
                self.items.insert(
                        index,
                        (item[0], item[1])
                )
            else:
                self.items.insert(
                        index,
                        (item, None)
                )

        self.buildFrame()

    def addItems(self, *items: Union[DirectGuiWidget,
                                     Tuple[DirectGuiWidget, Optional[Dict[str, float]]]]):
        """
        Add items to the scrolled list, then we auto arrange them

        :param items: All items
        """
        for item in items:
            if isinstance(item, tuple):
                # If it's a tuple, we have added some sort of offset
                self.items.append(
                        (item[0], item[1])
                )
            else:
                self.items.append(
                        (item, None)
                )

        self.buildFrame()

    def buildFrame(self):
        """
        arranges the items into the frame
        """
        self.ignoreAll()
        self.accept(f'press-wheel_up-{self.guiId}', self.__scrollUp)
        self.accept(f'press-wheel_down-{self.guiId}', self.__scrollDown)
        z = self['itemMargin'][1] + self['itemPadding']/2.
        for item, offsets in self.items:
            x = self['itemMargin'][0]
            z -= self['itemPadding']
            if offsets is not None:
                x += offsets.get('xOffset', 0)
                z -= offsets.get('zOffset', 0)

            item.reparentTo(self.canvas)
            item.setPos(x, 0, z)
            # stupid hack to allow scrolling while hovering over a btn
            if hasattr(item, 'guiId'):
                self.accept(f'press-wheel_up-{item.guiId}', self.__scrollUp)
                self.accept(f'press-wheel_down-{item.guiId}', self.__scrollDown)
            if self['useItemBoundsForPadding']:
                z -= item.getHeight()

        self['canvasSize'] = (-self['width'] + 0.05, self['width'] - 0.05, z - self['itemPadding']/2., 0)
