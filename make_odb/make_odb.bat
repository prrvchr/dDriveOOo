
cd .\vnd.dropbox-apps
..\..\zip.exe -0 vnd.dropbox-apps.zip mimetype
..\..\zip.exe -r vnd.dropbox-apps.zip *
cd ..

move /Y .\vnd.dropbox-apps\vnd.dropbox-apps.zip ..\DropboxOOo\vnd.dropbox-apps.odb
