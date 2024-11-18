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

from com.sun.star.logging.LogLevel import INFO

from com.sun.star.ucb import IllegalIdentifierException

from com.sun.star.rest.ParameterType import JSON

from .ucp import Provider as ProviderBase
from .ucp import g_ucboffice

from .dbtool import currentDateTimeInTZ
from .dbtool import currentUnoDateTime

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
from .configuration import g_pages
from .configuration import g_ucpfolder

import json
import ijson
import traceback
from mutagen._senf import sep


class Provider(ProviderBase):

    @property
    def BaseUrl(self):
        return g_url
    @property
    def Host(self):
        return g_host
    @property
    def Name(self):
        return g_provider
    @property
    def UploadUrl(self):
        return g_upload

    # Must be implemented method
    def getDocumentLocation(self, user, item):
        # XXX: Nothing to do here
        return item

    def getFirstPullRoots(self, user):
        return (user.RootId, )

    def getUser(self, source, request, name):
        return self._getUser(source, request)

    def mergeNewFolder(self, user, oldid, response):
        newid = None
        items = self._parseNewFolder(response)
        if all(items):
            newid = user.DataBase.updateNewItemId(user.Id, oldid, *items)
        return newid

    def parseFolder(self, user, data, parameter):
        return self.parseItems(user.Request, parameter, user.RootId)

    def parseItems(self, request, parameter, rootid):
        addchild = canrename = True
        trashed = readonly = versionable = False
        link = ''
        while parameter.hasNextPage():
            cursor = None
            response = request.execute(parameter)
            if response.Ok:
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
                            itemid = name = path = None
                            parents = ()
                            created = modified = currentUnoDateTime()
                            mimetype = g_ucpfolder
                            size = 0
                        elif (prefix, event) == ('entries.item.id', 'string'):
                            itemid = value
                        elif (prefix, event) == ('entries.item.name', 'string'):
                            name = value
                        elif (prefix, event) == ('entries.item.server_modified', 'string'):
                            created = self.parseDateTime(value)
                        elif (prefix, event) == ('entries.item.client_modified', 'string'):
                            modified = self.parseDateTime(value)
                        elif (prefix, event) == ('entries.item..tag', 'string'):
                            mimetype = g_ucpfolder if value == 'folder' else 'application/octet-stream'
                        elif (prefix, event) == ('entries.item.size', 'number'):
                            size = value
                        elif (prefix, event) == ('entries.item.path_display', 'string'):
                            part1, sep, part2 = value.rpartition('/')
                            if part1:
                                path = part1
                            else:
                                parents = (rootid, )
                        elif (prefix, event) == ('entries.item', 'end_map'):
                            if itemid and name:
                                yield {'Id': itemid,
                                       'Name': name,
                                       'DateCreated': created,
                                       'DateModified': modified,
                                       'MediaType': mimetype,
                                       'Size': size,
                                       'Link': link,
                                       'Trashed': trashed,
                                       'CanAddChild': addchild,
                                       'CanRename': canrename,
                                       'IsReadOnly': readonly,
                                       'IsVersionable': versionable,
                                       'Parents': parents,
                                       'Path': path}
                    del events[:]
                parser.close()
            response.close()

    def parseUploadLocation(self, response):
        location = response.getJson().getString('link')
        response.close()
        return location

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

    def updateItemId(self, user, oldid, response):
        newid = response.getJson().getString('id')
        response.close()
        if newid and oldid != newid:
            user.DataBase.updateItemId(user.Id, newid, oldid)
            self.updateNewItemId(oldid, newid)
        return newid

    # Private method
    def _getUser(self, source, request):
        parameter = self.getRequestParameter(request, 'getUser')
        response = request.execute(parameter)
        if not response.Ok:
            self.raiseIllegalIdentifierException(source, 561, parameter, response)
        return self._parseUser(response)

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

    def _parseUser(self, response):
        userid = name = displayname = rootid = None
        timestamp = currentUnoDateTime()
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
        return {'Id': userid,
                'Name': name,
                'DisplayName': displayname,
                'RootId': rootid,
                'DateCreated': timestamp,
                'DateModified': timestamp}

    # Requests get Parameter method
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
            path = '' if data.get('IsRoot') else data.get('Id')
            parameter.setJson('path', path)
            parameter.setJson('include_deleted', False)
            parameter.setJson('limit', g_pages)

        elif method == 'downloadFile':
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
            parameter.setJson('path', data.get('Path') + data.get('Title'))

        elif method == 'createNewFile':
            parameter.Method = 'POST'
            parameter.Url += '/file_requests/create'
            parameter.setJson('title', data.get('Title'))
            parameter.setJson('destination', data.get('Path'))

        # For parameter see: https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        elif method == 'getUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            parameter.setJson('commit_info/path', data.get('Path') + data.get('Title'))
            parameter.setJson('commit_info/mode', 'overwrite')
            parameter.setJson('duration', 3600)

        # For parameter see: https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        elif method == 'getNewUploadLocation':
            parameter.Method = 'POST'
            parameter.Url += '/files/get_temporary_upload_link'
            parameter.setJson('commit_info/path', data.get('Path') + data.get('Title'))
            parameter.setJson('commit_info/mode', 'add')
            parameter.setJson('duration', 3600)

        elif method == 'getUploadStream':
            parameter.Method = 'POST'
            parameter.Url = data
            parameter.NoAuth = True
            parameter.setHeader('Content-Type', 'application/octet-stream')

        return parameter

