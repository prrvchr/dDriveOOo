#!/bin/bash

cd ./make_odb
./make_odb.sh
cd ..

cd ./DropboxOOo/
zip -0 DropboxOOo.zip mimetype
zip -r DropboxOOo.zip *
cd ..

mv ./DropboxOOo/DropboxOOo.zip ./DropboxOOo.oxt
