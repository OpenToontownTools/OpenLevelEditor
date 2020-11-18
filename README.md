![thumbnail](https://i.imgur.com/Q722uK2.png)

## An open sourced modernized version of Disney's in-house Toontown Online level editor used to create .dna files.

# [***READ THE FAQ BEFORE ASKING QUESTIONS***](#faq)
### [Check the WIKI for help and showcases of what the community has made with this tool!](https://github.com/OpenToontownTools/TTOpenLevelEditor/wiki)

![overviewimage](https://i.imgur.com/i3RyBiu.png)


## Major New Features
* Fully Updated to Panda3D and Python 3
* A ton of smaller debug features
* Auto PDNA compiler support for libpandadna and corporate clash (legacy python libpandadna)
* A lot of usability improvements
* Modular zone system
   * Makes adding support for new zones INCREDIBLY easy
* [Automatic map creation](https://www.youtube.com/watch?v=B9HAfcF4_bE)
   * Renders image and calculates all needed data for $TOONTOWN/src/quest/QuestMapGlobals
   * All done with one press (Shift + F12)
* Server Specific Support
   * Currently includes specific options for Corporate Clash, with features for more servers coming
* And a lot more. You can check out a full list of every new feature by looking at the [changelogs](https://github.com/OpenToontownTools/TTOpenLevelEditor/releases)

## Upcoming Features
* Auto Saving
* and much more!

## Requirements
### ***IMPORTANT***
* **You need a Panda3D build that INCLUDES commit [b507c88](https://github.com/panda3d/panda3d/commit/b507c88cd9fd5d3a432aae42fdc9165422a527b4) and [7d14d52](https://github.com/panda3d/panda3d/commit/7d14d5275c826b5d02486b0d12eae5f0f9b6a2c6) as these are CRITICAL fixes for the editor. You will NOT be able to use it without these fixes!**
* Toontown phase files that include all the dna files. [These](https://github.com/open-toontown/resources) work fine. ***Toontown Rewritten's phase files do NOT contain .dna files since they use a completely different format, so you need to use them from elsewhere. Open-Toontown's resources are the closest to Toontown Online's that you can get, while also being completely updated and compatible with Panda3D 1.10.x.***
* Basic knowledge on how streets are setup
* Here you have two options:
    * The advanced option
        * Build yourself a copy of [libtoontown](https://github.com/OpenToontownTools/libtoontown), and drop the .pyd files in the root directory.
        * Recent Panda3D build (1.10.7 or later) running on *__Python 3__*. This editor is NOT compatible with Python 2.x and will NOT ever be made compatible as Python 2.x is no longer supported.
    * **OR** the easy option:
        * you can download [my copy](https://drive.google.com/file/d/1lJ-4Ce3qLvRnvZzHCPlXAM088pCK7qr2/view?usp=sharing) of panda with the compatible libtoontown files in there. Just drag Panda3D-1.11.0-Py39-x64 to your C drive root directory and the libotp.pyd and libtoontown.pyd files to the root level editor directory. Note that the PYD files in here are ONLY compatible with MY copy of panda, so if you are using any other build you have to rebuild them yourself.

~~### You can also pick up a pre-built build in the releases tab~~ *Coming Soon*

## Credits
* [drewcification](https://github.com/drewc5131) - Project Lead | Developer
* [Disyer](https://github.com/darktohka/) - Updating [LIBTOONTOWN](https://github.com/darktohka/libtoontown) to be compatible with modern panda and python 3 | Other Assistance
* [Any other contributors are listed on the side](https://github.com/OpenToontownTools/TTOpenLevelEditor/graphs/contributors)

## Help
* If you encounter a bug, create an issue and attach the .dna file (and any models required). *If this is private information that you do not want to share on this public repo, feel free to send me a DM on discord @drewcification#5131*

* [*Please only contact me if you need assistance with the editor. No, I will not help you hack Toontown.*](https://cdn.discordapp.com/attachments/735304945062117468/760296465498898491/hwW1Mlq.png)

## Known Incompatibilities
~~* Corporate Clash's Acorn Acres street buildings (and likely YOTT as well)~~
   ~~* This is an issue we are investigating. Substitute them with another playground's buildings in the storage dna file. This issue occurs in all released versions of the level editor as well.~~ This issue is fixed in [recent commits to libtoontown](https://github.com/OpenToontownTools/libtoontown)

# FAQ
### Why can't I load a street from X playground?
* Make sure the hood's storage file is loaded. You do this by adding it to the `--hoods` launch option. For example, if you want to work on a street in Donald's Dock and another in Minnie's Melodyland, you set the launch option `-hoods DD ML`

### Do I have to credit the use of this editor?
* There is NO requirement to list this editor anywhere in your game credits, but you definitely can do so to spread the word!
* I do ask however, that should you make a modification to the editor, that you fork the editor and leave it open source to promote open source software for the community.

### What are the controls?
* Under the HELP drop-down menu at the top of the window, press the CONTROLS button and a popup will appear.

### Some of my props are using textures as if they were in a different playground?
* This is OK. This is just because you have support for more than 1 playground loaded. This is only visible in the editor, but I recommend you only load the zone you are working on.

### I did the setup properly, but the editor just closes on startup with no error message, how do I fix?
* If you are downloading my redistributed copy of Panda from above, this may be an issue of having multiple installations of panda, and an incorrect one being targeted. Try one or both of the following:
    * Edit the registry
        * Open RegEdit
        * Navigate to `Computer\HKEY_CURRENT_USER\SOFTWARE\Python\PythonCore\3.9\InstallPath`
        * Change (Default)'s value to `C:\Panda3D-1.11.0-py39-x64\python`
        * Change ExecutablePath's value to `C:\Panda3D-1.11.0-py39-x64\python\python.exe`
        * Save, and if that does not work try restarting your PC, or doing option #2
    * Remove all other versions of Panda3D.
