import AppKit

from mechanic2.mechanicTools import remember


class MCExtensionCirleCell(AppKit.NSActionCell):

    def drawWithFrame_inView_(self, frame, view):
        controller = self.objectValue()
        obj = controller.extensionObject()

        if obj.isExtensionInstalled():
            if obj.isExtensionFromStore() and obj.extensionStoreKey() is None:
                image = NotBoughtIndicator()
            elif obj.extensionNeedsUpdate():
                image = UpdateIndicator()
            else:
                image = InstalledIndicator()
            size = image.size()
            x = frame.origin.x + (frame.size.width - size.width) / 2 + 2
            y = frame.origin.y + (frame.size.height - size.height) / 2 - 1
            image.drawAtPoint_fromRect_operation_fraction_(
                (x, y),
                ((0, 0), (9, 9)),
                AppKit.NSCompositeSourceOver,
                1.0
            )


@remember
def NotBoughtIndicator():
    width = 9
    height = 9
    image = AppKit.NSImage.alloc().initWithSize_((width, height))
    image.lockFocus()

    path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(((3, 6), (3, 3)))
    path.appendBezierPathWithRect_(((3.5, 0), (2, 5)))

    path.addClip()

    color1 = AppKit.NSColor.redColor()
    color2 = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.1)

    color1.set()
    path.fill()

    color2.set()
    path.setLineWidth_(2)
    path.stroke()

    image.unlockFocus()

    return image


@remember
def InstalledIndicator():
    width = 9
    height = 9
    image = AppKit.NSImage.alloc().initWithSize_((width, height))
    image.lockFocus()

    path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(((0, 0), (9, 9)))
    path.addClip()

    color1 = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.4)
    color2 = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.1)

    color1.set()
    path.fill()

    color2.set()
    path.setLineWidth_(2)
    path.stroke()

    image.unlockFocus()

    return image


@remember
def UpdateIndicator():
    width = 9
    height = 9
    image = AppKit.NSImage.alloc().initWithSize_((width, height))
    image.lockFocus()

    path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(((0, 0), (9, 9)))
    path.addClip()
    color1 = AppKit.NSColor.orangeColor()

    color1.set()
    path.setLineWidth_(5)
    path.stroke()

    image.unlockFocus()

    return image


class MCImageTextFieldCell(AppKit.NSTextFieldCell):

    def drawWithFrame_inView_(self, frame, view):
        controller = self.objectValue()
        obj = controller.extensionObject()

        image = obj.extensionIcon()
        if image:
            rowHeight = view.rowHeight()
            imageFrame = frame.copy()
            imageFrame.size.width = rowHeight
            imageFrame.size.height = rowHeight
            frame.origin.x += rowHeight + 5
            frame.size.width -= rowHeight + 5
        super(MCImageTextFieldCell, self).drawWithFrame_inView_(frame, view)
        if image:
            image.drawInRect_(imageFrame)
