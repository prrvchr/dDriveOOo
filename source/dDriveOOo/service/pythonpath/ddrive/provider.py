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

from .ucp import Provider as ProviderBase

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

import json
from . import ijson
import traceback


class Provider(ProviderBase):
    def __init__(self, ctx, folder, link, logger):
        super(Provider, self).__init__(ctx, folder, link, logger)

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
    @property
    def DateTimeFormat(self):
        return '%Y-%m-%dT%H:%M:%SZ'
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

    def getUser(self, source, request, name):
        user = self._getUser(source, request, name)
        root = self._getRoot(user[-1])
        return user, root

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

    def getDocumentLocation(self, content):
        # FIXME: This method being also called by the replicator,
        # FIXME: we must provide a dictionary
        return content.MetaData

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
        print("Provider.parseItem() 1 Method: %s" % parameter.Name)
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

    def parseRootFolder(self, parameter, content):
        return self.parseItems(content.User.Request, parameter, (content.Id, ))

    def parseItems(self, request, parameter, parents=()):
        while parameter.hasNextPage():
            cursor = None
            response = request.execute(parameter)
            if not response.Ok:
                break
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('cursor', 'string'):
                        parameter.SyncToken = value
                    elif (prefix, event) == ('has_more', 'boolean'):
                        if value:
                            parameter.setNextPage('cursor', parameter.SyncToken, JSON)
                    elif (prefix, event) == ('entries.item', 'start_map'):
                        itemid = name = None
                        created = modified = currentUnoDateTime()
                        mimetype = g_folder
                        size = 0
                        addchild = canrename = True
                        trashed = readonly = versionable = False
                        path = None
                    elif (prefix, event) == ('entries.item.id', 'string'):
                        itemid = value
                    elif (prefix, event) == ('entries.item.name', 'string'):
                        name = value
                    elif (prefix, event) == ('entries.item.server_modified', 'string'):
                        created = self.parseDateTime(value)
                    elif (prefix, event) == ('entries.item.client_modified', 'string'):
                        modified = self.parseDateTime(value)
                    elif (prefix, event) == ('entries.item..tag', 'string'):
                        mimetype = g_folder if value == 'folder' else 'application/octet-stream'
                    elif (prefix, event) == ('entries.item.size', 'number'):
                        size = value
                    elif (prefix, event) == ('entries.item.path_display', 'string'):
                        if not parents:
                            path, sep, tmp = value.rpartition('/')
                    elif (prefix, event) == ('entries.item', 'end_map'):
                        yield itemid, name, created, modified, mimetype, size, False, True, True, False, False, path, parents
                del events[:]
            parser.close()
            response.close()

    def parseUploadLocation(self, response):
        url =  None
        if response.Ok:
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('link', 'string'):
                        url = value
                del events[:]
            parser.close()
        response.close()
        return url

    def updateItemId(self, database, oldid, response):
        if response is not None:
            if response.Ok:
                newid = self._parseNewId(response)
                if newid and oldid != newid:
                    database.updateItemId(newid, oldid)
                return newid
            response.close()
        return None

    def _parseNewId(self, response):
        newid = None
        events = ijson.sendable_list()
        parser = ijson.parse_coro(events)
        iterator = response.iterContent(g_chunk, False)
        while iterator.hasMoreElements():
            parser.send(iterator.nextElement().value)
            for prefix, event, value in events:
                if (prefix, event) == ('id', 'string'):
                    newid = value
            del events[:]
        parser.close()
        response.close()
        return newid

    def mergeNewFolder(self, user, oldid, response):
        item = self._parseNewFolder(response)
        if all(item):
            return user.DataBase.updateNewItemId(oldid, *item)
        return None

    def _parseNewFolder(self, response):
        newid = created = modified = None
        if response.Ok:
            created = modified = currentUnoDateTime()
            events = ijson.sendable_list()
            parser = ijson.parse_coro(events)
            iterator = response.iterContent(g_chunk, False)
            while iterator.hasMoreElements():
                parser.send(iterator.nextElement().value)
                for prefix, event, value in events:
                    if (prefix, event) == ('metadata.id', 'string'):
                        newid = value
                del events[:]
            parser.close()
        response.close()
        return newid, created, modified

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
            parameter.NextUrl += '/files/list_folder/continue'
            parameter.setJson('path', '')
            parameter.setJson('recursive', True)
            parameter.setJson('include_deleted', False)

        elif method == 'getToken':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder/get_latest_cursor'
            parameter.setJson('path', '')
            parameter.setJson('recursive', True)
            parameter.setJson('include_deleted', False)

        elif method == 'getPull':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder/continue'
            parameter.NextUrl += '/files/list_folder/continue'
            parameter.setJson('cursor', data.Token)

        elif method == 'getFolderContent':
            parameter.Method = 'POST'
            parameter.Url += '/files/list_folder'
            parameter.NextUrl += '/files/list_folder/continue'
            path = '' if data.IsRoot else data.Id
            parameter.setJson('path', path)
            parameter.setJson('include_deleted', False)
            parameter.setJson('limit', g_pages)

        elif method == 'getDocumentContent':
            parameter.Method = 'POST'
            parameter.Url = self.UploadUrl + '/files/download'
            parameter.setHeader('Dropbox-API-Arg', '{"path": "%s"}' % data.get('Id'))

        elif method == 'updateTitle':
            parameter.Method = 'POST'
            parameter.Url += '/files/move_v2'
            path = '' if data.get('AtRoot') else data.get('ParentId')
            parameter.setJson('from_path', data.get('Id'))
            parameter.setJson('to_path', path + '/' + data.get('Title'))

        elif method == 'updateTrashed':
            parameter.Method = 'POST'
            parameter.Url += '/files/delete_v2'
            parameter.setJson('path', data.get('Id'))

        elif method == 'updateParents':
            parameter.Method = 'PATCH'
            parameter.Url += '/files/' + data.get('Id')
            toadd = data.get('ParentToAdd')
            toremove = data.get('ParentToRemove')
            if len(toadd) > 0:
                parameter.setJson('addParents', ','.join(toadd))
            if len(toremove) > 0:
                parameter.setJson('removeParents', ','.join(toremove))

        elif method == 'createNewFolder':
            parameter.Method = 'POST'
            parameter.Url += '/files/create_folder_v2'
            parameter.setJson('path', data.get('Path') + '/' + data.get('Title'))

        elif method == 'createNewFile':
            parameter.Method = 'POST'
            parameter.Url += '/file_requests/create'
            parameter.setJson('title', data.get('Title'))
            parameter.setJson('destination', data.get('Path'))

        elif method == 'getUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            parameter.setNesting('commit_info/path', data.get('Id'))
            parameter.setNesting('commit_info/mode', 'overwrite')
            parameter.setNesting('commit_info/mute', True)

        elif method == 'getNewUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            parameter.setNesting('commit_info/path', data.get('Path') + '/' + data.get('Title'))
            parameter.setNesting('commit_info/mode', 'add')
            parameter.setNesting('commit_info/mute', True)

        elif method == 'getUploadStream':
            parameter.Method = 'POST'
            parameter.Url = data
            parameter.setHeader('Content-Type', 'application/octet-stream')

        return parameter

