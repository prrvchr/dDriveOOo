#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import uno
import unohelper

from com.sun.star.beans import XPropertiesChangeNotifier

from com.sun.star.beans.PropertyAttribute import BOUND
from com.sun.star.beans.PropertyAttribute import CONSTRAINED
from com.sun.star.beans.PropertyAttribute import READONLY
from com.sun.star.beans.PropertyAttribute import TRANSIENT

from com.sun.star.container import XChild

from com.sun.star.lang import NoSupportException
from com.sun.star.lang import XComponent

from com.sun.star.ucb import CommandAbortedException
from com.sun.star.ucb import IllegalIdentifierException
from com.sun.star.ucb import InteractiveBadTransferURLException
from com.sun.star.ucb import XCommandProcessor2
from com.sun.star.ucb import XContent
from com.sun.star.ucb import XContentCreator

from com.sun.star.ucb.ContentAction import INSERTED
from com.sun.star.ucb.ContentAction import EXCHANGED

from com.sun.star.ucb.ContentInfoAttribute import KIND_DOCUMENT
from com.sun.star.ucb.ContentInfoAttribute import KIND_FOLDER
from com.sun.star.ucb.ContentInfoAttribute import KIND_LINK

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from ..unolib import PropertySetInfo

from ..unotool import createService
from ..unotool import getSimpleFile
from ..unotool import getProperty
from ..unotool import hasInterface

from .contentlib import CommandInfo
from .contentlib import Row
from .contentlib import DynamicResultSet

from .contentcore import getPropertiesValues
from .contentcore import setPropertiesValues

from .contenttools import getCommandInfo
from .contenttools import getContentEvent
from .contenttools import getContentInfo
from .contenttools import getMimeType

from .contentidentifier import ContentIdentifier

from ..logger import getLogger

from ..configuration import g_defaultlog
from ..configuration import g_scheme

import traceback
from oauthlib.uri_validate import authority


class Content(unohelper.Base,
              XContent,
              XComponent,
              XCommandProcessor2,
              XContentCreator,
              XChild,
              XPropertiesChangeNotifier):
    def __init__(self, ctx, user, authority, identifier, uri, data=None):
        self._ctx = ctx
        self._user = user
        self._authority = authority
        self._identifier = identifier
        self._new = data is not None
        self._contentListeners = []
        self._propertiesListener = {}
        self._listeners = []
        self._logger = user._logger
        self.MetaData = data if self._new else self._getMetaData(uri)
        self._commandInfo = self._getCommandInfo()
        self._propertySetInfo = self._getPropertySetInfo()
        self._logger.logprb(INFO, 'Content', '__init__()', 501)

    @property
    def IsFolder(self):
        return self.MetaData.getValue('IsFolder')
    @property
    def IsDocument(self):
        return self.MetaData.getValue('IsDocument')
    @property
    def CanAddChild(self):
        return self.MetaData.getValue('CanAddChild')

    @property
    def Uri(self):
        return self.MetaData.getDefaultValue('Uri', None)
    @property
    def Id(self):
        return self.MetaData.getDefaultValue('Id', None)
    @property
    def ParentId(self):
        return self.MetaData.getDefaultValue('ParentId', None)
    @property
    def ParentUri(self):
        return self.MetaData.getDefaultValue('ParentUri', None)

    def isRoot(self):
        return self.Id == self._user.RootId

    def setProperties(self, identifier, authority):
        self._identifier = identifier
        self._authority = authority

    # XComponent
    def dispose(self):
        event = uno.createUnoStruct('com.sun.star.lang.EventObject')
        event.Source = self
        for listener in self._listeners:
            print("Content.dispose() ***************************************************************")
            listener.disposing(event)

    def addEventListener(self, listener):
        self._listeners.append(listener)

    def removeEventListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    # XChild
    def getParent(self):
        try:
            content = None
            print("Content.getParent() 1 ParentUri: %s" % self.ParentUri)
            if not self.isRoot():
                url = self._user.getContentUrl(self._authority, self.ParentUri)
                identifier = ContentIdentifier(url)
                print("Content.getParent() 2")
                content = self._user.getContent(identifier, self.ParentUri, self._authority)
            print("Content.getParent() 3")
            return content
        except Exception as e:
            msg = "Error: %s" % traceback.print_exc()
            print(msg)

    def setParent(self, parent):
        raise NoSupportException('Parent can not be set', self)

    # XPropertiesChangeNotifier
    def addPropertiesChangeListener(self, names, listener):
        for name in names:
            if name not in self._propertiesListener:
                self._propertiesListener[name] = []
            if listener not in self._propertiesListener[name]:
                self._propertiesListener[name].append(listener)
    def removePropertiesChangeListener(self, names, listener):
        for name in names:
            if name in self._propertiesListener:
                if listener in self._propertiesListener[name]:
                    self._propertiesListener[name].remove(listener)

    # XContentCreator
    def queryCreatableContentsInfo(self):
        return self._user.getCreatableContentsInfo(self.CanAddChild)
    def createNewContent(self, info):
        # To avoid circular imports, the creation of new content is delegated to
        # ContentUser.createNewContent() since the ContentUser also creates Content
        # with ContentUser.createContent()
        print("Content.createNewContent() 1")
        return self._user.createNewContent(self.Id, self.Uri, self._authority, info.Type)

    # XContent
    def getIdentifier(self):
        return self._identifier
    def getContentType(self):
        return self.MetaData.getValue('ContentType')
    def addContentEventListener(self, listener):
        print("Content.addContentEventListener() ***************************************************************")
        self._contentListeners.append(listener)
    def removeContentEventListener(self, listener):
        if listener in self._contentListeners:
            self._contentListeners.remove(listener)

    # XCommandProcessor2
    def createCommandIdentifier(self):
        print("Content.createCommandIdentifier() 1")
        return 1
    def execute(self, command, id, environment):
        print("Content.execute() 1  Commande Name: %s ****************************************************************" % command.Name)
        print("Content.execute() %s - %s - %s" % (command.Name, self.Uri, self.Id))
        msg = "command.Name: %s" % command.Name
        self._logger.logp(INFO, 'Content', 'execute()', msg)
        if command.Name == 'getCommandInfo':
            return CommandInfo(self._getCommandInfo())
        elif command.Name == 'getPropertySetInfo':
            return PropertySetInfo(self._propertySetInfo)
        elif command.Name == 'getPropertyValues':
            values = getPropertiesValues(self._logger, self, command.Argument)
            return Row(values)
        elif command.Name == 'setPropertyValues':
            return setPropertiesValues(self._logger, self, environment, command.Argument)
        elif command.Name == 'delete':
            self.MetaData.insertValue('Trashed', True)
            self._user.DataBase.updateContent(self._user.Id, self.Id, 'Trashed', True)
        elif command.Name == 'open':
            print("Content.execute() open  Mode: %s" % command.Argument.Mode)
            if self.IsFolder:
                print("Content.execute() open 1")
                select = self._user.getFolderContent(self.MetaData, command.Argument.Properties, self._authority)
                print("Content.execute() open 2")
                msg += " IsFolder: %s" % self.IsFolder
                self._logger.logp(INFO, 'Content', 'execute()', msg)
                print("Content.execute() open 3")
                return DynamicResultSet(self._user, select)
            elif self.IsDocument:
                print("Content.execute() open 4")
                sf = getSimpleFile(self._ctx)
                url, size = self._user.getDocumentContent(sf, self.MetaData, 0)
                if not size:
                    title = self.MetaData.getValue('Title')
                    msg = "Error while downloading file: %s" % title
                    print("Content.execute() %s" % msg)
                    raise CommandAbortedException(msg, self)
                sink = command.Argument.Sink
                isreadonly = self.MetaData.getValue('IsReadOnly')
                if hasInterface(sink, 'com.sun.star.io.XActiveDataSink'):
                    sink.setInputStream(sf.openFileRead(url))
                elif not isreadonly and hasInterface(sink, 'com.sun.star.io.XActiveDataStreamer'):
                    sink.setStream(sf.openFileReadWrite(url))
        elif command.Name == 'insert':
            # The Insert command is only used to create a new folder or a new document
            # (ie: File Save As).
            # It saves the content created by 'createNewContent' from the parent folder
            # right after the Title property is initialized
            print("Content.execute() insert 1 - %s - %s - %s" % (self.IsFolder,
                                                                 self.Id,
                                                                 self.MetaData.getValue('Title')))
            if self.IsFolder:
                print("Content.execute() insert 2 ************** %s" % self.MetaData.getValue('MediaType'))
                try:
                    if self._user.insertNewContent(self.MetaData):
                        print("Content.execute() insert 3")
                        # Need to consum the new Identifier if needed...
                        self._user.deleteNewIdentifier(self.Id)
                        print("Content.execute() insert 4")
                except Exception as e:
                    msg = "Content.Insert() Error: %s" % traceback.print_exc()
                    print(msg)
                    raise e
                        
            elif self.IsDocument:
                stream = command.Argument.Data
                replace = command.Argument.ReplaceExisting
                sf = getSimpleFile(self._ctx)
                url = self._user.Provider.SourceURL
                target = '%s/%s' % (url, self.Id)
                if sf.exists(target) and not replace:
                    return
                if hasInterface(stream, 'com.sun.star.io.XInputStream'):
                    sf.writeFile(target, stream)
                    # For document type resources, the media type is always unknown...
                    mediatype = getMimeType(self._ctx, stream)
                    self.MetaData.setValue('MediaType', mediatype)
                    stream.closeInput()
                    print("Content.execute() insert 2 ************** %s" % mediatype)
                    if self._user.insertNewContent(self.MetaData):
                        # Need to consum the new Identifier if needed...
                        self._user.deleteNewIdentifier(self.Id)
                        print("Content.execute() insert 3")

        elif command.Name == 'createNewContent' and self.IsFolder:
            return self.createNewContent(command.Argument)
        elif command.Name == 'transfer' and self.IsFolder:
            # Transfer command is used for document 'File Save' or 'File Save As'
            # NewTitle come from:
            # - Last segment path of 'XContent.getIdentifier().getContentIdentifier()' for OpenOffice
            # - Property 'Title' of 'XContent' for LibreOffice
            # If the content has been renamed, the last segment is the new Title of the content
            title = command.Argument.NewTitle
            source = command.Argument.SourceURL
            move = command.Argument.MoveData
            clash = command.Argument.NameClash
            print("Content.execute() transfert 1 %s - %s -%s - %s" % (title, source, move, clash))
            # We check if 'NewTitle' is a child of this folder by recovering its ItemId
            itemid = self._user.DataBase.getChildId(self.Id, title)
            if itemid is None:
                print("Content.execute() transfert 2 %s" % itemid)
                # ItemId could not be found: 'NewTitle' does not exist in the folder...
                # For new document (File Save As) we use commands:
                # - createNewContent: for creating an empty new Content
                # - Insert at new Content for committing change
                # To execute these commands, we must throw an exception
                msg = "Couln't handle Url: %s" % source
                raise InteractiveBadTransferURLException(msg, self)
            print("Content.execute() transfert 3 %s - %s" % (itemid, source))
            sf = getSimpleFile(self._ctx)
            if not sf.exists(source):
                raise CommandAbortedException("Error while saving file: %s" % source, self)
            inputstream = sf.openFileRead(source)
            target = '%s/%s' % (self._user.Provider.SourceURL, itemid)
            sf.writeFile(target, inputstream)
            inputstream.closeInput()
            # We need to update the Size
            self._user.DataBase.updateContent(self._user.Id, itemid, 'Size', sf.getSize(target))
            if move:
                pass #must delete object
        elif command.Name == 'flush' and self.IsFolder:
            pass

    def abort(self, id):
        pass
    def releaseCommandIdentifier(self, id):
        pass

    # Private methods
    def _getMetaData(self, uri):
        print("Content._getMetaData() Uri: '%s'" % uri)
        if uri:
            itemid, isroot = self._user.DataBase.getIdentifier(self._user, uri)
        else:
            itemid, isroot = self._user.RootId, True
        print("Content._getMetaData() ItemId: '%s'" % itemid)
        if itemid is None:
            msg = self._logger.resolveString(511, uri)
            raise IllegalIdentifierException(msg, self)
        data = self._user.DataBase.getItem(self._user.Id, itemid, isroot)
        if data is None:
            msg = self._logger.resolveString(512, itemid, uri)
            print("Content._getMetaData() ERREUR ID: %s - Uri: '%s'" % (itemid, uri))
            raise IllegalIdentifierException(msg, self)
        data.insertValue('Uri', uri)
        return data

    def _getCommandInfo(self):
        commands = {}
        t1 = uno.getTypeByName('com.sun.star.ucb.XCommandInfo')
        commands['getCommandInfo'] = getCommandInfo('getCommandInfo', t1)
        t2 = uno.getTypeByName('com.sun.star.beans.XPropertySetInfo')
        commands['getPropertySetInfo'] = getCommandInfo('getPropertySetInfo', t2)
        t3 = uno.getTypeByName('[]com.sun.star.beans.Property')
        commands['getPropertyValues'] = getCommandInfo('getPropertyValues', t3)
        t4 = uno.getTypeByName('[]com.sun.star.beans.PropertyValue')
        commands['setPropertyValues'] = getCommandInfo('setPropertyValues', t4)
        try:
            t5 = uno.getTypeByName('com.sun.star.ucb.OpenCommandArgument3')
        except RuntimeError as e:
            t5 = uno.getTypeByName('com.sun.star.ucb.OpenCommandArgument2')
        commands['open'] = getCommandInfo('open', t5)
        try:
            t6 = uno.getTypeByName('com.sun.star.ucb.InsertCommandArgument2')
        except RuntimeError as e:
            t6 = uno.getTypeByName('com.sun.star.ucb.InsertCommandArgument')
        commands['insert'] = getCommandInfo('insert', t6)
        if not self.isRoot():
            commands['delete'] = getCommandInfo('delete', uno.getTypeByName('boolean'))
        try:
            t7 = uno.getTypeByName('com.sun.star.ucb.TransferInfo2')
        except RuntimeError as e:
            t7 = uno.getTypeByName('com.sun.star.ucb.TransferInfo')
        commands['transfer'] = getCommandInfo('transfer', t7)
        commands['flush'] = getCommandInfo('flush')
        print("Content._getCommandInfo() CanAddChild: %s   **********************************************" % self.CanAddChild)
        if self.CanAddChild:
            t8 = uno.getTypeByName('com.sun.star.ucb.ContentInfo')
            commands['createNewContent'] = getCommandInfo('createNewContent', t8)
        return commands

    def _getPropertySetInfo(self):
        RO = 0 if self._new else READONLY
        properties = {}
        properties['ContentType'] = getProperty('ContentType', 'string', BOUND | RO)
        properties['MediaType'] = getProperty('MediaType', 'string', BOUND | READONLY)
        properties['IsDocument'] = getProperty('IsDocument', 'boolean', BOUND | RO)
        properties['IsFolder'] = getProperty('IsFolder', 'boolean', BOUND | RO)
        properties['Title'] = getProperty('Title', 'string', BOUND | CONSTRAINED)
        properties['Size'] = getProperty('Size', 'long', BOUND | RO)
        created = getProperty('DateCreated', 'com.sun.star.util.DateTime', BOUND | READONLY)
        properties['DateCreated'] = created
        modified = getProperty('DateModified', 'com.sun.star.util.DateTime', BOUND | RO)
        properties['DateModified'] = modified
        properties['IsReadOnly'] = getProperty('IsReadOnly', 'boolean', BOUND | RO)
        info = getProperty('CreatableContentsInfo','[]com.sun.star.ucb.ContentInfo', BOUND | RO)
        properties['CreatableContentsInfo'] = info
        properties['CasePreservingURL'] = getProperty('CasePreservingURL', 'string', BOUND | RO)
        properties['BaseURI'] = getProperty('BaseURI', 'string', BOUND | READONLY)
        properties['TitleOnServer'] = getProperty('TitleOnServer', 'string', BOUND)
        properties['IsHidden'] = getProperty('IsHidden', 'boolean', BOUND | RO)
        properties['IsVolume'] = getProperty('IsVolume', 'boolean', BOUND | RO)
        properties['IsRemote'] = getProperty('IsRemote', 'boolean', BOUND | RO)
        properties['IsRemoveable'] = getProperty('IsRemoveable', 'boolean', BOUND | RO)
        properties['IsFloppy'] = getProperty('IsFloppy', 'boolean', BOUND | RO)
        properties['IsCompactDisc'] = getProperty('IsCompactDisc', 'boolean', BOUND | RO)
        properties['IsVersionable'] = getProperty('IsVersionable', 'boolean', BOUND | RO)
        return properties

    def _setTitle(self, title):
        try:
            # If Title change we need to change Identifier.getContentIdentifier()
            print("Identifier.setTitle() 1 New Title: %s - New: %s" % (title, self._new))
            if not self._new:
                # And as the uri changes we also have to clear this Identifier from the cache.
                # New Identifier bypass the cache: they are created by the folder's Identifier
                # (ie: createNewIdentifier()) and have same uri as this folder.
                self._user.expireContent(self.Uri)
            if self._user.Provider.SupportDuplicate:
                newtitle = self._user.DataBase.getNewTitle(title, self.ParentId, self.IsFolder)
            else:
                newtitle = title
            print("Identifier.setTitle() 2 Title: %s - New Title: %s" % (title, newtitle))
            url = '%s/%s' % (self.ParentUri, newtitle)
            self.MetaData.setValue('Uri', url)
            self.MetaData.setValue('Title', newtitle)
            self.MetaData.setValue('TitleOnServer', newtitle)
            # If the identifier is new then the content is not yet in the database.
            # It will be inserted by the insert command of the XCommandProcessor2.execute()
            if not self._new:
                self._user.DataBase.updateContent(self._user.Id, self.Id, 'Title', title)
            print("Identifier.setTitle() 3 Title")
        except Exception as e:
            msg = "Identifier.setTitle() Error: %s" % traceback.print_exc()
            print(msg)
