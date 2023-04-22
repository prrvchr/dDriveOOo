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

from com.sun.star.ucb import IllegalIdentifierException

from com.sun.star.rest.ParameterType import JSON

from .providerbase import ProviderBase

from .dbtool import currentUnoDateTime
from .dbtool import currentDateTimeInTZ

from .unotool import getResourceLocation

from .configuration import g_identifier
from .configuration import g_scheme
from .configuration import g_provider
from .configuration import g_host
from .configuration import g_url
from .configuration import g_upload
from .configuration import g_userfields
from .configuration import g_drivefields
from .configuration import g_itemfields
from .configuration import g_chunk
from .configuration import g_folder
from .configuration import g_office
from .configuration import g_link
from .configuration import g_doc_map
from .configuration import g_pages

from . import ijson
import traceback


class Provider(ProviderBase):
    def __init__(self, ctx, folder, link, logger):
        self._ctx = ctx
        self._folder = folder
        self._link = link
        self._logger = logger
        self.Scheme = g_scheme
        self.SourceURL = getResourceLocation(ctx, g_identifier, g_scheme)
        self._folders = []

    @property
    def Name(self):
        return g_provider
    @property
    def Host(self):
        return g_host
    @property
    def BaseUrl(self):
        return g_url
    @property
    def UploadUrl(self):
        return g_upload
    @property
    def Office(self):
        return g_office
    @property
    def Document(self):
        return g_doc_map
    def DateTimeFormat(self):
        return '%Y-%m-%dT%H:%M:%S.%fZ'
    @property
    def Folder(self):
        return self._folder
    @property
    def Link(self):
        return self._link

    def getFirstPullRoots(self, user):
        return (user.RootId, )

    def initUser(self, database, user, token):
        # FIXME: Some APIs like Dropbox allow to have the token during the firstPull
        #token = self.getUserToken(user)
        if database.updateToken(user.Id, token):
            user.setToken(token)

    def pullUser(self, user):
        timestamp = currentDateTimeInTZ()
        parameter = self.getRequestParameter(user.Request, 'getPull', user)
        iterator = self.parseItems(user.Request, parameter)
        count = user.DataBase.mergeItems(user.Id, iterator)
        return parameter.SyncToken, count, parameter.PageCount


    def parseUserToken(self, response):
        token = None
        events = ijson.sendable_list()
        parser = ijson.parse_coro(events)
        iterator = response.iterContent(g_chunk, False)
        while iterator.hasMoreElements():
            parser.send(iterator.nextElement().value)
            for prefix, event, value in events:
                if (prefix, event) == ('cursor', 'string'):
                    token = value
            del events[:]
        parser.close()
        return token

    def getUser(self, source, request, name):
        user = self._getUser(source, request, name)
        root = self._getRoot(user[-1])
        print("Provider.getUser() UserId: %s - RootId: %s" % (user[0], user[-1]))
        return user, root

    def getDocumentLocation(self, content):
        return content

    def _getUser(self, source, request, name):
        parameter = self.getRequestParameter(request, 'getUser')
        response = request.execute(parameter)
        if not response.Ok:
            msg = self._logger.resolveString(403, name)
            raise IllegalIdentifierException(msg, source)
        return self._parseUser(response)

    def _getRoot(self, rootid):
        timestamp = currentUnoDateTime()
        return rootid, 'Homework', timestamp, timestamp, g_folder, False, True, False, False, False

    def _parseUser(self, response):
        userid = name = displayname = rootid = None
        events = ijson.sendable_list()
        parser = ijson.parse_coro(events)
        iterator = response.iterContent(g_chunk, False)
        while iterator.hasMoreElements():
            parser.send(iterator.nextElement().value)
            for prefix, event, value in events:
                if (prefix, event) == ('account_id', 'string'):
                    userid = value
                elif (prefix, event) == ('email', 'string'):
                    name = value
                elif (prefix, event) == ('name.display_name', 'string'):
                    displayname = value
                elif (prefix, event) == ('root_info.root_namespace_id', 'string'):
                    rootid = value
            del events[:]
        parser.close()
        response.close()
        return userid, name, displayname, rootid

    def _parseItem(self, request, parameter):
        while parameter.hasNextPage():
            response = request.execute(parameter)
            if not response.Ok:
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                chunk = iterator.nextElement().value
                print("Provider._parseItem() Content: \n%s" % chunk.decode('utf-8'))
                parser.send(chunk)
                for prefix, event, value in events:
                    print("Provider._parseItem() Prefix: %s - Event: %s - Value: %s" % (prefix, event, value))
                    if (prefix, event) == ('id', 'string'):
                        itemid = value
                    elif (prefix, event) == ('name', 'string'):
                        name = value
                    elif (prefix, event) == ('server_modified', 'string'):
                        created = self.parseDateTime(value)
                    elif (prefix, event) == ('client_modified', 'string'):
                        modified = self.parseDateTime(value)
                del events[:]
            parser.close()
        response.close()
        return itemid, name, created, modified, g_folder, False, True, False, False, False


    def parseItems(self, request, parameter):
        print("Provider.parseItems() 1 Method: %s" % parameter.Name)
        while parameter.hasNextPage():
            print("Provider.parseItems() 1 Method: %s" % parameter.Name)
            cursor = None
            response = request.execute(parameter)
            print("Provider.parseItems() 2 Method: %s - Encoding: %s - StatusCode: %s - Url:\n%s" % (parameter.Name, response.ApparentEncoding, response.StatusCode, parameter.Url))
            if not response.Ok:
                print("Provider.parseItems() Text: %s" % response.Text)
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                chunk = iterator.nextElement().value
                print("Provider.parseItems() 3 Method: %s- Page: %s - Content\n'%s'" % (parameter.Name, parameter.PageCount, chunk.decode('ascii')))
                parser.send(chunk)
                for prefix, event, value in events:
                    #print("Provider.parseItems() Prefix: %s - Event: %s - Value: %s" % (prefix, event, value))
                    if (prefix, event) == ('cursor', 'string'):
                        cursor = value
                    elif (prefix, event) == ('has_more', 'boolean'):
                        if value and cursor is not None:
                            parameter.setNextPage('cursor', cursor, JSON)
                    elif (prefix, event) == ('value.item', 'start_map'):
                        itemid = name = None
                        created = modified = currentUnoDateTime()
                        mimetype = g_folder
                        size = 0
                        addchild = canrename = True
                        trashed = readonly = versionable = False
                        parents = []
                    elif (prefix, event) == ('value.item.id', 'string'):
                        itemid = value
                    elif (prefix, event) == ('value.item.name', 'string'):
                        name = value
                    elif (prefix, event) == ('value.item.createdDateTime', 'string'):
                        created = self.parseDateTime(value)
                    elif (prefix, event) == ('value.item.lastModifiedDateTime', 'string'):
                        modified = self.parseDateTime(value)
                    elif (prefix, event) == ('value.item.file.mimeType', 'string'):
                        mimetype = value
                    elif (prefix, event) == ('value.item.trashed', 'boolean'):
                        trashed = value
                    elif (prefix, event) == ('value.item.size', 'string'):
                        size = int(value)
                    elif (prefix, event) == ('value.item.parentReference.id', 'string'):
                        parents.append(value)
                    elif (prefix, event) == ('value.item', 'end_map'):
                        yield itemid, name, created, modified, mimetype, size, trashed, True, True, False, False, parents
                del events[:]
            parser.close()
            response.close()


    def getRequestParameter(self, request, method, data=None):
        parameter = request.getRequestParameter(method)
        parameter.Url = self.BaseUrl
        parameter.NextUrl = self.BaseUrl
        if method == 'getUser':
            parameter.Method = 'POST'
            parameter.Url += '/users/get_current_account'


        elif method == 'getItem':
            parameter.Method = 'POST'
            parameter.Url += '/file_requests/get'
            parameter.setJson('id', data)

        elif method == 'getFirstPull':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder'
            parameter.setJson('path', '')
            parameter.setJson('recursive', True)
            parameter.setJson('include_deleted', False)
            
            #token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            #token.Type = TOKEN_URL | TOKEN_JSON
            #token.Field = 'cursor'
            #token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            #token.IsConditional = True
            #token.ConditionField = 'has_more'
            #token.ConditionValue = True
            #enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            #enumerator.Field = 'entries'
            #enumerator.Token = token
            #parameter.Enumerator = enumerator

        elif method == 'getToken':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder/get_latest_cursor'
            parameter.setJson('path', '')
            parameter.setJson('recursive', True)
            parameter.setJson('include_deleted', False)

        elif method == 'getPull':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder/continue'
            parameter.setJson('cursor', data.Token)
            #token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            #token.Type = TOKEN_JSON | TOKEN_SYNC
            #token.Field = 'cursor'
            #token.SyncField = ''
            #token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            #token.IsConditional = True
            #token.ConditionField = 'has_more'
            #token.ConditionValue = True
            #enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            #enumerator.Field = 'entries'
            #enumerator.Token = token
            #parameter.Enumerator = enumerator

        elif method == 'getFolderContent':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder'
            parameter.NextUrl += '/files/list_folder/continue'
            path = '' if data.IsRoot else data.Id
            parameter.setJson('path', path)
            parameter.setJson('include_deleted', False)
            parameter.setJson('limit', g_pages)

            #token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            #token.Type = TOKEN_URL | TOKEN_JSON
            #token.Field = 'cursor'
            #token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            #token.IsConditional = True
            #token.ConditionField = 'has_more'
            #token.ConditionValue = True
            #enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            #enumerator.Field = 'entries'
            #enumerator.Token = token
            #parameter.Enumerator = enumerator

        elif method == 'getDocumentContent':
            parameter.Method = 'POST'
            parameter.Url = f'{self.UploadUrl}/files/download'
            path = '{\\"path\\": \\"%s\\"}' % data.Id
            parameter.setHeader('Dropbox-API-Arg', path)

        elif method == 'updateTitle':
            parameter.Method = 'POST'
            parameter.Url += '/files/move_v2'
            path = '' if data.get('AtRoot') else data.get('ParentId')
            parameter.setJson('from_path', data.get('Id'))
            parameter.setJson('to_path', f"{path}/{data.get('Title')}")

        elif method == 'updateTrashed':
            parameter.Method = 'POST'
            parameter.Url += '/files/delete_v2'
            parameter.setJson('path', data.get('Id'))

        elif method == 'updateParents':
            parameter.Method = 'PATCH'
            parameter.Url += f"/files/{data.get('Id')}"
            toadd = data.get('ParentToAdd')
            toremove = data.get('ParentToRemove')
            if len(toadd) > 0:
                parameter.setJson('addParents', ','.join(toadd))
            if len(toremove) > 0:
                parameter.setJson('removeParents', ','.join(toremove))

        elif method == 'createNewFolder':
            parameter.Method = 'POST'
            parameter.Url += '/files/create_folder_v2'
            path = '' if data.get('AtRoot') else data.get('ParentId')
            parameter.setJson('path', f"{path}/{data.get('Title')}")

        elif method == 'createNewFile':
            parameter.Method = 'POST'
            parameter.Url += '/file_requests/create'
            path = '' if data.get('AtRoot') else data.get('ParentId')
            parameter.setJson('title', data.get('Title'))
            parameter.setJson('destination', f"{path}/{data.get('Title')}")

        elif method == 'getUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            parameter.setNesting('commit_info/path', data.get('Id'))
            parameter.setNesting('commit_info/mode', 'overwrite')
            parameter.setNesting('commit_info/mute', True)

        elif method == 'getNewUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            path = '' if data.get('AtRoot') else data.get('ParentId')
            parameter.setNesting('commit_info/path', f"{path}/{data.get('Title')}")
            parameter.setNesting('commit_info/mode', 'add')
            parameter.setNesting('commit_info/mute', True)

        elif method == 'getUploadStream':
            parameter.Method = 'POST'
            parameter.Url = data.get('link')
            parameter.setHeader('Content-Type', 'application/octet-stream')
        return parameter


    def getItemParent(self, item, rootid):
        ref = item.getDefaultValue('parentReference', KeyMap())
        parent = ref.getDefaultValue('id', rootid)
        return (parent, )

    def getRootId(self, item):
        return self.getItemId(item)
    def getRootTitle(self, item):
        return self.getItemTitle(item)
    def getRootCreated(self, item, timestamp=None):
        return toUnoDateTime(timestamp)
    def getRootModified(self, item, timestamp=None):
        return toUnoDateTime(timestamp)
    def getRootMediaType(self, item):
        return self.Folder
    def getRootSize(self, item):
        return 0
    def getRootTrashed(self, item):
        return False
    def getRootCanAddChild(self, item):
        return True
    def getRootCanRename(self, item):
        return False
    def getRootIsReadOnly(self, item):
        return False
    def getRootIsVersionable(self, item):
        return False

    def getItemId(self, item):
        return item.getDefaultValue('id', None)
    def getItemTitle(self, item):
        return item.getDefaultValue('name', None)
    def getItemCreated(self, item, timestamp=None):
        created = item.getDefaultValue('server_modified', None)
        if created:
            return self.parseDateTime(created, '%Y-%m-%dT%H:%M:%SZ')
        return toUnoDateTime(timestamp)
    def getItemModified(self, item, timestamp=None):
        modified = item.getDefaultValue('client_modified', None)
        if modified:
            return self.parseDateTime(modified, '%Y-%m-%dT%H:%M:%SZ')
        return toUnoDateTime(timestamp)
    def getItemMediaType(self, item):
        tag = item.getDefaultValue('.tag', 'folder')
        return 'application/octet-stream' if tag != 'folder' else self.Folder
    def getItemSize(self, item):
        return int(item.getDefaultValue('size', 0))
    def getItemTrashed(self, item):
        return item.getDefaultValue('trashed', False)
    def getItemCanAddChild(self, item):
        return True
    def getItemCanRename(self, item):
        return True
    def getItemIsReadOnly(self, item):
        return False
    def getItemIsVersionable(self, item):
        return False

    def getResponseId(self, response, default):
        id = response.getDefaultValue('metadata', KeyMap()).getDefaultValue('id', None)
        if id is None:
            id = default
        return id
    def getResponseTitle(self, response, default):
        title = response.getDefaultValue('metadata', KeyMap()).getDefaultValue('name', None)
        if title is None:
            title = default
        return title

    def getRoot(self, request, user):
        id = user.getValue('root_info').getValue('root_namespace_id')
        root = KeyMap()
        root.insertValue('id', id)
        root.insertValue('name', 'Homework')
        response = uno.createUnoStruct('com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>')
        response.IsPresent = True
        response.Value = root
        return response

    def createFile(self, request, uploader, item):
        parameter = self.getRequestParameter('createNewFile', item)
        response = request.execute(parameter)
        if response.IsPresent:
            return True
        return False

