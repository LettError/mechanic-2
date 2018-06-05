from AppKit import *
import json

import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController

from mojo.extensions import getExtensionDefault

from mechanic2.ui.cells import MCExtensionCirleCell, MCImageTextFieldCell
from mechanic2.ui.formatters import MCExtensionDescriptionFormatter
from mechanic2.ui.settings import Settings, extensionStoreDataURL
from mechanic2.extensionItem import ExtensionRepository, ExtensionStoreItem, ExtensionYamlItem
from mechanic2.mechacnicTools import getDataFromURL


class MCExtensionListItem(NSObject):

    def __new__(cls, *args, **kwargs):
        return cls.alloc().init()

    def __init__(self, extensionObject=None):
        self._extensionObject = extensionObject

    def copyWithZone_(self, zone):
        new = self.__class__.allocWithZone_(zone).init()
        new._extensionObject = self._extensionObject
        return new

    def extensionController(self):
        return self

    def extensionObject(self):
        return self._extensionObject

    def extensionSearchString(self):
        return self._extensionObject.extensionSearchString()


def getExtensionData(url):
    try:
        extensionData = getDataFromURL(url, formatter=json.loads)
    except Exception as e:
        print(e)
        extensionData = dict()
    return extensionData.get("extensions", [])


class MechanicController(BaseWindowController):

    def __init__(self, shouldLoad=True):

        self.w = vanilla.Window((600, 300), "Mechanic 2.0", minSize=(550, 200))

        # building toolbar
        self._toolbarSearch = vanilla.SearchBox((0, 0, 300, 0), callback=self.toolbarSearch)
        self._toolbarSearch.getNSSearchField().setFrame_(((0, 0), (300, 22)))

        toolbarItems = [
            dict(
                itemIdentifier="search",
                label="Search",
                view=self._toolbarSearch.getNSSearchField(),
            ),
            dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            dict(
                itemIdentifier="settings",
                label="Settings",
                imageNamed="prefToolbarMisc",
                callback=self.toolbarSettings,
            ),
        ]

        self.w.addToolbar(toolbarIdentifier="MechanicToolbar", toolbarItems=toolbarItems, addStandardItems=False, displayMode="icon")

        # building extension list

        columnDescriptions = columnDescriptions = [
            dict(title="", key="extensionController", width=25, cell=MCExtensionCirleCell.alloc().init(), editable=False),
            dict(title="Extension", key="extensionController",
                cell=MCImageTextFieldCell.alloc().init(),
                formatter=MCExtensionDescriptionFormatter.alloc().init(),
                editable=False),
        ]

        self.w.extensionList = vanilla.List((0, 0, -0, -38),
            [],
            columnDescriptions=columnDescriptions,
            showColumnTitles=False,
            selectionCallback=self.extensionListSelectionCallback,
            doubleClickCallback=self.extensionListDoubleClickCallback,
            allowsMultipleSelection=False,
            rowHeight=39
        )

        self.w.button = vanilla.Button((-150, -30, -10, 22), "Install", callback=self.buttonCallback)
        self.w.uninstall = vanilla.Button((-280, -30, -160, 22), "Uninstall", callback=self.uninstallCallback)

        self.w.extensionList.setSelection([])
        self.w.open()

        if shouldLoad:
            self.loadExtensions()

    def loadExtensions(self):
        progress = self.startProgress("Loading extensions...")

        try:
            wrappedItems = []
            for urlStream in getExtensionDefault("com.mechanic.urlstreams"):
                clss = ExtensionRepository
                if urlStream == extensionStoreDataURL:
                    clss = ExtensionStoreItem
                for data in getExtensionData(urlStream):
                    try:
                        item = MCExtensionListItem(clss(data))
                        wrappedItems.append(item)
                    except Exception as error:
                        print(error)

            for singleExtension in getExtensionDefault("com.mechanic.singleExtensionItems"):
                try:
                    item = MCExtensionListItem(ExtensionYamlItem(singleExtension))
                    wrappedItems.append(item)
                except Exception as error:
                    print(error)

            progress.update("Setting Extensions...")
            self.w.extensionList.set(wrappedItems)
        except Exception as error:
            print(error)
        progress.close()

    def extensionListSelectionCallback(self, sender):
        item = self.getSelection()
        if item is None:
            self.w.button.setTitle("Install")
            self.w.button.enable(False)
            self.w.uninstall.enable(False)
        else:
            self.w.button.enable(True)
            self.w.uninstall.enable(item.isExtensionInstalled())

            if item.isExtensionFromStore():
                self.w.button.setTitle("Purchase")
            else:
                self.w.button.setTitle("Install")

    def extensionListDoubleClickCallback(self, sender):
        item = self.getSelection()
        if item:
            item.openRemoteURL()

    # buttons

    def buttonCallback(self, sender):
        item = self.getSelection()
        if item is None:
            return

        if item.isExtensionFromStore():
            item.openRemotePurchageURL()
        else:
            item.remoteInstall()
            self.w.extensionList.getNSTableView().reloadData()

    def uninstallCallback(self, sender):
        item = self.getSelection()
        if item is None:
            return
        item.extensionUninstall()
        self.w.extensionList.getNSTableView().reloadData()

    def settingsCallback(self, sender):
        self.loadExtensions()

    # toolbar

    def toolbarSettings(self, sender):
        Settings(self.w, callback=self.settingsCallback)

    def toolbarSearch(self, sender):
        search = sender.get()
        arrayController = self.w.extensionList.getNSTableView().dataSource()
        if not search:
            arrayController.setFilterPredicate_(None)
        else:
            search = 'extensionSearchString CONTAINS "%s"' % search.lower()
            predicate = NSPredicate.predicateWithFormat_(search)
            arrayController.setFilterPredicate_(predicate)

    # helpers

    def getSelection(self):
        arrayController = self.w.extensionList.getNSTableView().dataSource()
        selection = arrayController.selectedObjects()
        if selection:
            return selection[0].extensionObject()
        return None
