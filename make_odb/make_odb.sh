#!/bin/bash

cd ./vnd.dropbox-apps/
zip -0 vnd.dropbox-apps.zip mimetype
zip -r vnd.dropbox-apps.zip *
cd ..

mv ./vnd.dropbox-apps/vnd.dropbox-apps.zip ../DropboxOOo/vnd.dropbox-apps.odb
