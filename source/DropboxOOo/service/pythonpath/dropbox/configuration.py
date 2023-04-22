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

# Provider configuration
g_scheme = 'vnd-dropbox'
g_extension = 'DropboxOOo'
g_identifier = 'io.github.prrvchr.%s' % g_extension

g_provider = 'Dropbox'
g_host = 'api.dropboxapi.com'
g_version = '2'
g_url = 'https://%s/%s' % (g_host, g_version)
g_upload = 'https://content.dropboxapi.com/2'

g_userfields = 'id,userPrincipalName,displayName'
g_drivefields = 'id,createdDateTime,lastModifiedDateTime,name'
g_itemfields = '%s,file,size,parentReference' % g_drivefields
g_pages = 10

# Data chunk: 327680 (320Ko) is the Request iter_content() buffer_size, must be a multiple of 64
g_chunk = 320 * 1024

g_office = 'application/vnd.oasis.opendocument'
g_folder = 'application/vnd.dropbox-apps.folder'
g_link = 'application/vnd.dropbox-apps.link'
g_doc_map = {'application/vnd.microsoft-apps.document':     'application/vnd.oasis.opendocument.text',
             'application/vnd.microsoft-apps.spreadsheet':  'application/x-vnd.oasis.opendocument.spreadsheet',
             'application/vnd.microsoft-apps.presentation': 'application/vnd.oasis.opendocument.presentation',
             'application/vnd.microsoft-apps.drawing':      'application/pdf'}

g_cache = 20
g_admin = False

# The URL separator
g_separator = '/'

# Resource strings files folder
g_resource = 'resource'
# Logging required global variable
g_basename = 'ContentProvider'
g_defaultlog = 'DropboxLog'
g_errorlog = 'DropboxError'
# Logging global variable
g_synclog = 'DropboxSync'

