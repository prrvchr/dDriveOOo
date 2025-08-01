<!--
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
-->
# Documentation

**This [document][3] in English.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'utilisation][4] et à notre [Politique de protection des données][5].**

# version [1.3.1][6]

## Introduction:

**dDriveOOo** fait partie d'une [Suite][7] d'extensions [LibreOffice][8] ~~et/ou [OpenOffice][9]~~ permettant de vous offrir des services inovants dans ces suites bureautique.

Cette extension vous permet de travailler dans LibreOffice sur vos fichiers Dropbox, même hors ligne.  
Elle utilise [l'API Dropbox][10] pour synchroniser vos fichier Dropbox distant avec l'aide d'une base de données locale HsqlDB 2.7.2.  
Cette extension est vu par LibreOffice comme un [fournisseur de contenu][11] (Content Provider) répondant à l'URL: `vnd-dropbox://*`.

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][12].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][13] si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Prérequis:

L'extension dDriveOOo utilise l'extension OAuth2OOo pour fonctionner.  
Elle doit donc répondre aux [prérequis de l'extension OAuth2OOo][14].

L'extension dDriveOOo utilise l'extension jdbcDriverOOo pour fonctionner.  
Elle doit donc répondre aux [prérequis de l'extension jdbcDriverOOo][15].  
De plus, dDriveOOo nécessite que l'extension jdbcDriverOOo soit configurée pour fournir `com.sun.star.sdb` comme niveau d'API, qui est la configuration par défaut.

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- [![OAuth2OOo logo][17]][18] Installer l'extension **[OAuth2OOo.oxt][19]** [![Version][20]][19]

    Vous devez d'abord installer cette extension, si elle n'est pas déjà installée.

- [![jdbcDriverOOo logo][21]][22] Installer l'extension **[jdbcDriverOOo.oxt][23]** [![Version][24]][23]

    Vous devez installer cette extension, si elle n'est pas déjà installée.

- ![dDriveOOo logo][25] Installer l'extension **[dDriveOOo.oxt][26]** [![Version][27]][26]

Redémarrez LibreOffice après l'installation.  
**Attention, redémarrer LibreOffice peut ne pas suffire.**
- **Sous Windows** pour vous assurer que LibreOffice redémarre correctement, utilisez le Gestionnaire de tâche de Windows pour vérifier qu'aucun service LibreOffice n'est visible après l'arrêt de LibreOffice (et tuez-le si ç'est le cas).
- **Sous Linux ou macOS** vous pouvez également vous assurer que LibreOffice redémarre correctement, en le lançant depuis un terminal avec la commande `soffice` et en utilisant la combinaison de touches `Ctrl + C` si après l'arrêt de LibreOffice, le terminal n'est pas actif (pas d'invité de commande).

___

## Utilisation:

**Ouvrir vos fichiers Dropbox:**

Dans: **Fichier -> Ouvrir** saisir dans la première liste déroulante:

- Pour une Url nommée: **vnd-dropbox://votre_adresse@votre_fournisseur**  

ou

- Pour une url non nommée (anonyme): **vnd-dropbox:///**

Et validez non pas par le bouton **Ouvrir** mais par la touche **Entrée**.

Si vous ne donnez pas **votre_adresse@votre_fournisseur**, elle vous sera demandée...

Les Urls anonymes vous permettent de rester anonyme (votre compte n'apparaît pas dans l'Url) tandis que les Urls nommées vous permettent d'accéder à plusieurs comptes simultanément.

Après avoir autorisé l'application [OAuth2OOo][18] à accéder à vos fichiers Dropbox, vos fichiers Dropbox devraient apparaître!!! normalement  :wink:

___

## Comment personnaliser les menus de LibreOffice:

Afin de pouvoir conserver l'utilisation des fenêtres de dialogue système pour l'ouverture et l'enregistrement des fichiers dans LibreOffice, il est désormais possible de créer des menus personnalisés pour les commandes: **Ouvrir distant** et **Enregistrer distant**.

Dans l'onglet **Menu** de la fenêtre **Outils -> Personnaliser**, sélectionnez **Macros** dans **Catégorie** pour accéder aux deux macros: `OpenRemote` et `SaveRemote` sous: **Mes macros -> dDriveOOo**.  
Il faudra d'abord ajouter la macro `OpenRemote` à l'un des menus avec l'**Étendue** définie sur **LibreOffice**, puis il faudra ouvrir les applications (Writer, Calc, Draw...) éventuellement en ouvrant un nouveau document, et ajouter les macros `OpenRemote` et `SaveRemote` avec l'**Étendue** définie sur l'application à laquelle vous souhaitez ajouter les menus.

La macro `OpenRemote` prend en charge tout type d'**Étendue**, tandis que la macro `SaveRemote` ne doit être attribuée qu'aux étendues de type application car elle nécessite qu'un document soit déjà ouvert dans LibreOffice.  
Cela ne doit être fait qu'une seule fois pour LibreOffice et chaque application, et malheureusement je n'ai encore rien trouvé de plus simple.

___

## Comment créer l'extension:

Normalement, l'extension est créée avec Eclipse pour Java et [LOEclipse][28]. Pour contourner Eclipse, j'ai modifié LOEclipse afin de permettre la création de l'extension avec Apache Ant.  
Pour créer l'extension dDriveOOo avec l'aide d'Apache Ant, vous devez:
- Installer le [SDK Java][29] version 8 ou supérieure.
- Installer [Apache Ant][30] version 1.10.0 ou supérieure.
- Installer [LibreOffice et son SDK][31] version 7.x ou supérieure.
- Cloner le dépôt [dDriveOOo][32] sur GitHub dans un dossier.
- Depuis ce dossier, accédez au répertoire: `source/dDriveOOo/`
- Dans ce répertoire, modifiez le fichier `build.properties` afin que les propriétés `office.install.dir` et `sdk.dir` pointent vers les dossiers d'installation de LibreOffice et de son SDK, respectivement.
- Lancez la création de l'archive avec la commande: `ant`
- Vous trouverez l'archive générée dans le sous-dossier: `dist/`

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 24.8.0.3 (X86_64) - Windows 10(x64) - Python version 3.9.19 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][33]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][13]  
J'essaierai de le résoudre :smile:

___

## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Intégration et utilisation de la nouvelle version de Hsqldb 2.5.1.

- Ecriture d'une nouvelle interface [Replicator][34], lancé en arrière-plan (python Thread) responsable de:

    - Effectuer les procédures nécessaires lors de la création d'un nouvel utilisateur (Pull initial).

    - Effectuer des pulls régulièrement (toutes les dix minutes) afin de synchroniser les modifications externes (Tirer toutes les modifications).

    - Répliquer à la demande toutes les modifications apportées à la base de données hsqldb 2.5.1 à l'aide du contrôle de version du système (Pousser toutes les modifications).

- Ecriture d'une nouvelle interface [DataBase][35], responsable de tous les appels à la base de données.

- Mise en place d'un cache sur les identifiants, voir la méthode: [_getUser()][36], autorisant l'accès à un Contenu (fichier ou dossier) sans accès à la base de données pour les appels ultérieurs.

- Gestion des doublons des noms des fichiers / dossiers par [Vues SQL][37]: Child, Twin, Uri, et Title générant des noms uniques s'il existe des doublons.  
Bien que cette fonctionnalité ne soit nécessaire que pour gDriveOOo, elle est implémentée globalement...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Utilisation du nouveau schéma: **vnd-dropbox://** comme revendiqué par [draft-king-vnd-urlscheme-03.txt][38]

- Aboutissement de la gestion des doublons des noms de fichiers / dossiers par des vues SQL dans HsqlDB:
    - Une vue [**Twin**][39] regroupant tous les doublons par dossier parent et les ordonnant par date de création, date de modification.
    - Une vue [**Uri**][40] générant des indexes uniques pour chaque doublon.
    - Une vue [**Title**][41] générant des nom uniques pour chaque doublon.
    - Une vue récursive [**Path**][42] pour générer un chemin unique pour chaque fichier/dossier.

- Création d'un [Provider][43] capable de répondre aux deux types d'Urls supportées (nommées et anonymes).
  Des expressions régulières (regex), déclarées dans le [fichier de configuration de l'UCB][44], sont maintenant utilisées par OpenOffice/LibreOffice pour envoyer les Urls au ContentProvider approprié.

- Utilisation de la nouvelle struct UNO [DateTimeWithTimezone][45] fournie par l'extension [jdbcDriverOOo][22] depuis sa version 0.0.4.  
  Bien que cette struct existe déjà dans LibreOffice, sa création était nécessaire afin de rester compatible avec OpenOffice (voir [Demande d'amélioration 128560][46]).

- Modification de l'interface [Replicator][34], afin de permettre:
    - De choisir l'ordre de synchronisation des données (locales d'abord puis distantes ensuite ou inversement).
    - La synchronisation des modifications locales par des opérations atomiques effectuées dans l'ordre chronologique pour supporter pleinement le travail hors ligne.  
    Pour ce faire, trois procédures SQL [GetPushItems][47], [GetPushProperties][48] et [UpdatePushItems][49] sont utilisées pour chaque utilisateur ayant accédé à ses fichiers / dossiers.

- Réécriture de la [fenêtre des options][50] accessible par : **Outils -> Options -> Internet -> dDriveOOo** afin de permettre :
    - L'accès aux deux fichiers journaux concernant les activités de l'UCP et du réplicateur de données.
    - Le choix de l'ordre de synchronisation.
    - La modification de l'intervalle entre deux synchronisations.
    - L'accès à la base de données HsqlDB 2.7.2 sous-jacente gérant vos métadonnées Dropbox.

- La présence ou l'absence d'une barre oblique finale dans l'Url est maintenant prise en charge.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.1:

- Mise en place de la gestion des fichiers partagés.

- Le nom du dossier partagé peut être défini avant toute connexion dans: **Outils -> Options -> Internet -> dDriveOOo -> Gérer les documents partagés dans le dossier:**

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.2:

- L'absence ou l'obsolescence des extensions **OAuth2OOo** et/ou **jdbcDriverOOo** nécessaires au bon fonctionnement de **dDriveOOo** affiche désormais un message d'erreur.

- Encore plein d'autres choses...

### Ce qui a été fait pour la version 1.0.3:

- Prise en charge de la version 1.2.0 de l'extension **OAuth2OOo**. Les versions précédentes ne fonctionneront pas avec l'extension **OAuth2OOo** 1.2.0 ou ultérieure.

### Ce qui a été fait pour la version 1.0.4:

- Prise en charge de la version 1.2.1 de l'extension **OAuth2OOo**. Les versions précédentes ne fonctionneront pas avec l'extension **OAuth2OOo** 1.2.1 ou ultérieure.

### Ce qui a été fait pour la version 1.0.5:

- Prise en charge de la version 1.2.3 de l'extension **OAuth2OOo**. Correction du [dysfonctionnement #12][51].

### Ce qui a été fait pour la version 1.0.6:

- Prise en charge de la version 1.2.4 de l'extension **OAuth2OOo**. De nombreux problèmes résolus.

### Ce qui a été fait pour la version 1.0.7:

- Maintenant utilisation du package Python dateutil pour convertir vers UNO DateTime.

### Ce qui a été fait pour la version 1.1.0:

- Tous les paquets Python nécessaires à l'extension sont désormais enregistrés dans un fichier [requirements.txt][52] suivant la [PEP 508][53].
- Désormais si vous n'êtes pas sous Windows alors les paquets Python nécessaires à l'extension peuvent être facilement installés avec la commande:  
  `pip install requirements.txt`
- Modification de la section [Prérequis][54].

### Ce qui a été fait pour la version 1.1.1:

- Correction d'une régression empêchant la création de nouveaux fichiers.
- Intégration d'un correctif pour contourner le [dysfonctionnement #159988][55].

### Ce qui a été fait pour la version 1.1.2:

- La création de la base de données, lors de la première connexion, utilise l'API UNO proposée par l'extension jdbcDriverOOo depuis la version 1.3.2. Cela permet d'enregistrer toutes les informations nécessaires à la création de la base de données dans 6 tables texte qui sont en fait [6 fichiers csv][56].
- Réécriture des [vues SQL][57] nécessaires à la gestion des doublons. Désormais, le chemin d'un dossier ou d'un fichier est calculé par une vue récursive qui prend en charge les doublons.
- L'installation de l'extension désactivera l'option permettant de créer une copie de sauvegarde (ie: fichier .bak) dans LibreOffice. Si cette option est validée alors l'extension n'est plus capable d'enregistrer les fichiers.
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.4 et 1.3.2 minimum.
- De nombreuses corrections.

### Ce qui a été fait pour la version 1.1.3:

- Mise à jour du paquet [Python python-dateutil][58] vers la version 2.9.0.post0.
- Mise à jour du paquet [Python ijson][59] vers la version 3.3.0.
- Mise à jour du paquet [Python packaging][60] vers la version 24.1.
- Mise à jour du paquet [Python setuptools][61] vers la version 72.1.0 afin de répondre à l'[alerte de sécurité Dependabot][62].
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.6 et 1.4.2 minimum.

### Ce qui a été fait pour la version 1.1.4:

- Mise à jour du paquet [Python setuptools][61] vers la version 73.0.1.
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.7 et 1.4.5 minimum.
- Les modifications apportées aux options de l'extension, qui nécessitent un redémarrage de LibreOffice, entraîneront l'affichage d'un message.
- Support de LibreOffice version 24.8.x.

### Ce qui a été fait pour la version 1.1.5:

- Correction des paramètres de requête HTTP empêchant la mise à jour des fichiers sur les serveurs Dropbox.
- Correction d'une requête SQL empêchant la création correcte d'un nouveau dossier.
- La désactivation de la réplication des données dans les options d'extension affichera un message explicite dans le journal du réplicateur.
- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.3.8 et 1.4.6 minimum.
- Modification des options de l'extension accessibles via : **Outils -> Options... -> Internet -> dDriveOOo** afin de respecter la nouvelle charte graphique.

### Ce qui a été fait pour la version 1.1.6:

- Les modifications à distance du contenu des fichiers sont prises en compte par le réplicateur.
- Si nécessaire, il est possible de demander, dans les options de l'extension, une synchronisation initiale. Il est également possible de demander le téléchargement de tous les fichiers déjà visualisés qui ont une copie locale.
- Le réplicateur fournit une journalisation plus complète.
- De nombreuses corrections.

### Ce qui a été fait pour la version 1.2.0:

- L'extension vous demandera d'installer les extensions OAuth2OOo et jdbcDriverOOo en version respectivement 1.4.0 et 1.4.6 minimum.
- Il est possible de construire l'archive de l'extension (ie: le fichier oxt) avec l'utilitaire [Apache Ant][30] et le fichier script [build.xml][63].
- L'extension refusera de s'installer sous OpenOffice quelle que soit la version ou LibreOffice autre que 7.x ou supérieur.
- Ajout des fichiers binaires nécessaires aux bibliothèques Python pour fonctionner sous Linux et LibreOffice 24.8 (ie: Python 3.9).
- Afin d'utiliser un port arbitraire pour le retour du code d'autorisation OAuth2, l'URL de redirection passant par Github (ie: `https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/OAuth2Redirect`) est désormais utilisée.
- La possibilité de ne pas spécifier le nom du compte de l'utilisateur dans l'URL est à nouveau fonctionnelle.
- Ajout de la portée `files.content.read` aux droits OAuth2 requis par l'API Dropbox pour autoriser les téléchargements de fichiers.

### Ce qui a été fait pour la version 1.2.1:

- Mise à jour du paquet [Python packaging][60] vers la version 24.2.
- Mise à jour du paquet [Python setuptools][61] vers la version 75.8.0.
- Mise à jour du paquet [Python six][64] vers la version 1.17.0.
- Support de Python version 3.13.

### Ce qui a été fait pour la version 1.3.0:

- Mise à jour du paquet [Python packaging][60] vers la version 25.0.
- Rétrogradage du paquet [Python setuptools][61] vers la version 75.3.2, afin d'assurer la prise en charge de Python 3.8.
- Déploiement de l'enregistrement passif permettant une installation beaucoup plus rapide des extensions et de différencier les services UNO enregistrés de ceux fournis par une implémentation Java ou Python. Cet enregistrement passif est assuré par l'extension [LOEclipse][28] via les [PR#152][65] et [PR#157][66].
- Modification de [LOEclipse][28] pour prendre en charge le nouveau format de fichier `rdb` produit par l'utilitaire de compilation `unoidl-write`. Les fichiers `idl` ont été mis à jour pour prendre en charge les deux outils de compilation disponibles: idlc et unoidl-write.
- Il est désormais possible de créer le fichier oxt de l'extension dDriveOOo uniquement avec Apache Ant et une copie du dépôt GitHub. La section [Comment créer l'extension][67] a été ajoutée à la documentation.
- Implémentation de [PEP 570][68] dans la [journalisation][69] pour prendre en charge les arguments multiples uniques.
- Pour garantir la création correcte de la base de données dDriveOOo, il sera vérifié que l'extension jdbcDriverOOo a `com.sun.star.sdb` comme niveau d'API.
- Ecriture de deux macros `OpenRemote` et `SaveRemote` permettant de créer des menus personnalisés et de conserver la fenêtre de dialogue système pour l'ouverture et l'enregistrement de fichiers dans LibreOffice. Pour faciliter la création de ces menus personnalisés, la section [Comment personnaliser les menus de LibreOffice][70] a été ajoutée à la documentation.
- Nécessite l'extension **jdbcDriverOOo en version 1.5.0 minimum**.
- Nécessite l'extension **OAuth2OOo en version 1.5.0 minimum**.

### Ce qui a été fait pour la version 1.3.1:

- Support de LibreOffice 25.2.x et 25.8.x sous Windows 64 bits.
- Nécessite l'extension **jdbcDriverOOo en version 1.5.4 minimum**.
- Nécessite l'extension **OAuth2OOo en version 1.5.2 minimum**.

### Que reste-t-il à faire pour la version 1.3.1:

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: </img/drive.svg#collapse>
[2]: <https://prrvchr.github.io/dDriveOOo/>
[3]: <https://prrvchr.github.io/dDriveOOo>
[4]: <https://prrvchr.github.io/dDriveOOo/source/dDriveOOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/dDriveOOo/source/dDriveOOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/dDriveOOo/README_fr#ce-qui-a-%C3%A9t%C3%A9-fait-pour-la-version-131>
[7]: <https://prrvchr.github.io/README_fr>
[8]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[9]: <https://www.openoffice.org/fr/Telecharger/>
[10]: <https://www.dropbox.com/developers/documentation/http/documentation>
[11]: <https://wiki.openoffice.org/wiki/Documentation/DevGuide/UCB/Content_Providers>
[12]: <https://github.com/prrvchr/dDriveOOo>
[13]: <https://github.com/prrvchr/dDriveOOo/issues/new>
[14]: <https://prrvchr.github.io/OAuth2OOo/README_fr#pr%C3%A9requis>
[15]: <https://prrvchr.github.io/jdbcDriverOOo/README_fr#pr%C3%A9requis>
[17]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[18]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[19]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[20]: <https://img.shields.io/github/v/tag/prrvchr/OAuth2OOo?label=latest#right>
[21]: <https://prrvchr.github.io/jdbcDriverOOo/img/jdbcDriverOOo.svg#middle>
[22]: <https://prrvchr.github.io/jdbcDriverOOo/README_fr>
[23]: <https://github.com/prrvchr/jdbcDriverOOo/releases/latest/download/jdbcDriverOOo.oxt>
[24]: <https://img.shields.io/github/v/tag/prrvchr/jdbcDriverOOo?label=latest#right>
[25]: <img/dDriveOOo.svg#middle>
[26]: <https://github.com/prrvchr/dDriveOOo/releases/latest/download/dDriveOOo.oxt>
[27]: <https://img.shields.io/github/downloads/prrvchr/dDriveOOo/latest/total?label=v1.3.1#right>
[28]: <https://github.com/LibreOffice/loeclipse>
[29]: <https://adoptium.net/temurin/releases/?version=8&package=jdk>
[30]: <https://ant.apache.org/manual/install.html>
[31]: <https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.7.2/>
[32]: <https://github.com/prrvchr/dDriveOOo.git>
[33]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[34]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/replicator.py>
[35]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/database.py>
[36]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/datasource.py#L127>
[37]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py>
[38]: <https://datatracker.ietf.org/doc/html/draft-king-vnd-urlscheme-03>
[39]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L163>
[40]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L173>
[41]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L193>
[42]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L213>
[43]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/ucp/provider.py>
[44]: <https://github.com/prrvchr/dDriveOOo/blob/master/source/dDriveOOo/dDriveOOo.xcu#L42>
[45]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/rdb/idl/io/github/prrvchr/css/util/DateTimeWithTimezone.idl>
[46]: <https://bz.apache.org/ooo/show_bug.cgi?id=128560>
[47]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L512>
[48]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L557>
[49]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L494>
[50]: <https://github.com/prrvchr/dDriveOOo/tree/master/uno/lib/uno/options/ucb>
[51]: <https://github.com/prrvchr/gDriveOOo/issues/12>
[52]: <https://github.com/prrvchr/dDriveOOo/releases/latest/download/requirements.txt>
[53]: <https://peps.python.org/pep-0508/>
[54]: <https://prrvchr.github.io/mDriveOOo/README_fr#pr%C3%A9requis>
[55]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159988>
[56]: <https://github.com/prrvchr/dDriveOOo/tree/master/uno/lib/uno/ucb/hsqldb>
[57]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/ucb/dbqueries.py#L111>
[58]: <https://pypi.org/project/python-dateutil/>
[59]: <https://pypi.org/project/ijson/>
[61]: <https://pypi.org/project/packaging/>
[61]: <https://pypi.org/project/setuptools/>
[62]: <https://github.com/prrvchr/dDriveOOo/security/dependabot/1>
[63]: <https://github.com/prrvchr/dDriveOOo/blob/master/source/dDriveOOo/build.xml>
[64]: <https://pypi.org/project/six/>
[65]: <https://github.com/LibreOffice/loeclipse/pull/152>
[66]: <https://github.com/LibreOffice/loeclipse/pull/157>
[67]: <https://prrvchr.github.io/dDriveOOo/README_fr#comment-cr%C3%A9er-lextension>
[68]: <https://peps.python.org/pep-0570/>
[69]: <https://github.com/prrvchr/dDriveOOo/blob/master/uno/lib/uno/logger/logwrapper.py#L109>
[70]: <https://prrvchr.github.io/dDriveOOo/README_fr#comment-personnaliser-les-menus-de-libreoffice>
