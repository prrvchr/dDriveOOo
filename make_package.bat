
rem cd .\make_odb
rem call .\make_odb.bat
rem cd ..

cd .\DropboxOOo
..\zip.exe -0 DropboxOOo.zip mimetype
..\zip.exe -r DropboxOOo.zip *
cd ..

move /Y .\DropboxOOo\DropboxOOo.zip .\DropboxOOo.oxt
