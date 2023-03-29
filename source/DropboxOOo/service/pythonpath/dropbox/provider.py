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

from com.sun.star.ucb.ConnectionMode import OFFLINE

from com.sun.star.auth.RestRequestTokenType import TOKEN_NONE
from com.sun.star.auth.RestRequestTokenType import TOKEN_URL
from com.sun.star.auth.RestRequestTokenType import TOKEN_REDIRECT
from com.sun.star.auth.RestRequestTokenType import TOKEN_QUERY
from com.sun.star.auth.RestRequestTokenType import TOKEN_JSON
from com.sun.star.auth.RestRequestTokenType import TOKEN_SYNC

from .providerbase import ProviderBase

from .unolib import KeyMap

from .dbtool import toUnoDateTime

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
from .configuration import g_buffer
from .configuration import g_folder
from .configuration import g_office
from .configuration import g_link
from .configuration import g_doc_map


class Provider(ProviderBase):
    def __init__(self, ctx):
        self._ctx = ctx
        self.Scheme = g_scheme
        self.Link = ''
        self.Folder = ''
        self.SourceURL = ''
        self.SessionMode = OFFLINE
        self._Error = ''
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
    @property
    def Chunk(self):
        return g_chunk
    @property
    def Buffer(self):
        return g_buffer

    def getRequestParameter(self, method, data=None):
        parameter = uno.createUnoStruct('com.sun.star.auth.RestRequestParameter')
        parameter.Name = method
        if method == 'getUser':
            parameter.Method = 'POST'
            parameter.Url = '%s/users/get_current_account' % self.BaseUrl
        elif method == 'getItem':
            parameter.Method = 'POST'
            parameter.Url = '%s/file_requests/get' % self.BaseUrl
            #parameter.Data = '{"id": "%s"}' % data.getValue('Id')
            parameter.Json = '{"id": "%s"}' % data.getValue('Id')
        elif method == 'getFirstPull':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/list_folder' % self.BaseUrl
            parameter.Json = '{"path": "", "recursive": true, "include_deleted": false}'
            token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            token.Type = TOKEN_URL | TOKEN_JSON
            token.Field = 'cursor'
            token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            token.IsConditional = True
            token.ConditionField = 'has_more'
            token.ConditionValue = True
            enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            enumerator.Field = 'entries'
            enumerator.Token = token
            parameter.Enumerator = enumerator
        elif method == 'getToken':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/list_folder/get_latest_cursor' % self.BaseUrl
            parameter.Json = '{"path": "", "recursive": true, "include_deleted": false}'
        elif method == 'getPull':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/list_folder/continue' % self.BaseUrl
            parameter.Json = '{"cursor": "%s"}' % data.getValue('Token')
            token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            token.Type = TOKEN_JSON | TOKEN_SYNC
            token.Field = 'cursor'
            token.SyncField = ''
            token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            token.IsConditional = True
            token.ConditionField = 'has_more'
            token.ConditionValue = True
            enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            enumerator.Field = 'entries'
            enumerator.Token = token
            parameter.Enumerator = enumerator
        elif method == 'getFolderContent':
            print("Provider.getRequestParameter() %s" % ','.join(data.getKeys()))
            parameter.Method = 'POST'
            parameter.Url = '%s/files/list_folder' % self.BaseUrl
            path = '' if data.getValue('IsRoot') else data.getValue('Id')
            parameter.Json = '{"path": "%s", "include_deleted": false}' % path
            token = uno.createUnoStruct('com.sun.star.auth.RestRequestToken')
            token.Type = TOKEN_URL | TOKEN_JSON
            token.Field = 'cursor'
            token.Value = '%s/files/list_folder/continue' % self.BaseUrl
            token.IsConditional = True
            token.ConditionField = 'has_more'
            token.ConditionValue = True
            enumerator = uno.createUnoStruct('com.sun.star.auth.RestRequestEnumerator')
            enumerator.Field = 'entries'
            enumerator.Token = token
            parameter.Enumerator = enumerator
        elif method == 'getDocumentContent':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/download' % self.UploadUrl
            path = '{\\"path\\": \\"%s\\"}' % data.getValue('Id')
            parameter.Header = '{"Dropbox-API-Arg": "%s"}' % path
        elif method == 'updateTitle':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/move_v2' % self.BaseUrl
            path = '' if data.getValue('AtRoot') else data.getValue('ParentId')
            path += '/%s' % data.getValue('Title')
            parameter.Json = '{"from_path": "%s","to_path": "%s"}' % (data.getValue('Id'), path)
        elif method == 'updateTrashed':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/delete_v2' % self.BaseUrl
            parameter.Json = '{"path": "%s"}' % data.getValue('Id')

        elif method == 'updateParents':
            parameter.Method = 'PATCH'
            parameter.Url = '%s/files/%s' % (self.BaseUrl, data.getValue('Id'))
            toadd = data.getValue('ParentToAdd')
            toremove = data.getValue('ParentToRemove')
            if len(toadd) > 0:
                parameter.Json = '{"addParents": %s}' % ','.join(toadd)
            if len(toremove) > 0:
                parameter.Json = '{"removeParents": %s}' % ','.join(toremove)

        elif method == 'createNewFolder':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/create_folder_v2' % self.BaseUrl
            path = '' if data.getValue('AtRoot') else data.getValue('ParentId')
            path += '/%s' % data.getValue('Title')
            parameter.Json = '{"path": "%s"}' % path
        elif method == 'createNewFile':
            parameter.Method = 'POST'
            parameter.Url = '%s/file_requests/create' % self.BaseUrl
            title = data.getValue('Title')
            path = '' if data.getValue('AtRoot') else data.getValue('ParentId')
            path += '/%s' % title
            parameter.Json = '{"title": "%s", "destination": "%s"}' % (title, path)
        elif method == 'getUploadLocation':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/get_temporary_upload_link' % self.BaseUrl
            path = '"path": "%s"' % data.getValue('Id')
            mode = '"mode": "overwrite"'
            mute = '"mute": true'
            info = '{"commit_info": {%s, %s, %s}}' % (path, mode, mute)
            parameter.Json = info
        elif method == 'getNewUploadLocation':
            parameter.Method = 'POST'
            parameter.Url = '%s/files/get_temporary_upload_link' % self.BaseUrl
            path = '' if data.getValue('AtRoot') else data.getValue('ParentId')
            path += '/%s' % data.getValue('Title')
            path = '"path": "%s"' % path
            mode = '"mode": "add"'
            mute = '"mute": true'
            info = '{"commit_info": {%s, %s, %s}}' % (path, mode, mute)
            parameter.Json = info
        elif method == 'getUploadStream':
            parameter.Method = 'POST'
            parameter.Url = data.getValue('link')
            parameter.Header = '{"Content-Type": "application/octet-stream"}'
        return parameter

    def initUser(self, request, database, user):
        data = self.getToken(request, user)
        if data.IsPresent:
            token = self.getUserToken(data.Value)
            if database.updateToken(user.getValue('UserId'), token):
                user.setValue('Token', token)

    def getUserId(self, user):
        return user.getValue('account_id')
    def getUserName(self, user):
        return user.getValue('email')
    def getUserDisplayName(self, user):
        return user.getValue('name').getValue('display_name')
    def getUserToken(self, data):
        return data.getValue('cursor')

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
