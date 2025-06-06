#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb import IllegalIdentifierException

from .database import DataBase

from .oauth20 import getOAuth2UserName

from .unotool import getUriFactory

from .ucp import User

from .helper import getExceptionMessage
from .helper import showWarning

from .provider import Provider

from .replicator import Replicator

from .listener import CloseListener

from .configuration import g_extension

from threading import Event
from threading import Lock
import traceback


class DataSource():
    def __init__(self, ctx, logger, connection, url):
        cls, mtd = 'DataSource', '__init__'
        logger.logprb(INFO, cls, mtd, 301)
        self._ctx = ctx
        self._default = ''
        self._users = {}
        self._sync = Event()
        self._lock = Lock()
        self._urifactory = getUriFactory(ctx)
        self._database = DataBase(ctx, connection, url)
        self._provider = Provider(ctx, logger)
        self._replicator = Replicator(ctx, url, self._provider, self._users, self._sync, self._lock)
        self._logger = logger
        self._database.addCloseListener(CloseListener(self))
        logger.logprb(INFO, cls, mtd, 302)

    @property
    def DataBase(self):
        return self._database
    @property
    def Replicator(self):
        return self._replicator

    # called from XCloseListener
    def dispose(self):
        try:
            if self.Replicator.is_alive():
                self.Replicator.cancel()
            for user in self._users.values():
                user.dispose()
            self.DataBase.shutdownDataBase(self.Replicator.fullPull())
            self._logger.logprb(INFO, 'DataSource', 'dispose', 341, self._provider.Scheme)
        except Exception as e:
            self._logger.logprb(SEVERE, 'DataSource', 'dispose', 342, e, traceback.format_exc())

    # Get called from ContentProvider.queryContent()
    def queryContent(self, source, authority, url):
        user, uri = self._getUser(source, authority, url)
        if uri is None:
            msg = self._logger.resolveString(311, url)
            raise IllegalIdentifierException(msg, source)
        user.setLock()
        content = user.getContentByUri(authority, uri)
        if content is None:
            msg = self._logger.resolveString(311, url)
            raise IllegalIdentifierException(msg, source)
        return content

    # Get called from ContentProvider.compareContentIds()
    def getDefaultUser(self):
        return self._default

    def parseUrl(self, url):
        return self._urifactory.parse(url)

    # Private methods
    def _getUser(self, source, authority, url):
        default = False
        uri = self.parseUrl(url)
        if uri is None:
            msg = self._logger.resolveString(321, url)
            raise IllegalIdentifierException(msg, source)
        if authority:
            if uri.hasAuthority() and uri.getAuthority() != '':
                name = uri.getAuthority()
            else:
                title, msg = self._getExceptionMessage(322, url)
                showWarning(self._ctx, msg, title)
                raise IllegalIdentifierException(msg, source)
        elif self._default:
            name = self._default
        else:
            name = self._getUserName(source, url)
            default = True
        # XXX: User never change... we can cache it...
        if name in self._users:
            user = self._users[name]
            if not user.Request.isAuthorized():
                # XXX: The user's OAuth2 configuration has been deleted and
                # XXX: the OAuth2 configuration wizard has been canceled.
                title, msg = self._getExceptionMessage(324, name)
                showWarning(self._ctx, msg, title)
                raise IllegalIdentifierException(msg, source)
        else:
            user = User(self._ctx, source, self._logger, self.DataBase,
                        self._provider, self._sync, name)
            self._users[name] = user
        # XXX: If the user has been requested and instantiated
        # XXX: then we can consider it as the default user
        if default:
            self._default = name
        return user, uri

    def _getUserName(self, source, url):
        try:
            name = getOAuth2UserName(self._ctx, source, self._provider.Scheme)
        except Exception as e:
            print("DataSource._getUserName() ERROR: %s - %s" % (e, traceback.format_exc()))
        if not name:
            title, msg = self._getExceptionMessage(331, url)
            showWarning(self._ctx, msg, title)
            raise IllegalIdentifierException(msg, source)
        return name

    def _getExceptionMessage(self, code, *args):
        return getExceptionMessage(self._logger, code, g_extension, *args)
