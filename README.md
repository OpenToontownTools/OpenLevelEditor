# Toontown Open Level Editor
 
## An open sourced modernized version of Disney's in-house Toontown Online level editor used to create .dna files.

![overviewimage](https://i.imgur.com/4f7v8Ak.png)

## Requirements
### ***IMPORTANT***
* **You need a Panda3D build with [THIS](https://github.com/drewc5131/panda3d/commit/2b735df2d0b8f9880311a9a08a28c7ec684e9583) fix (You can just edit the .py file in your SDK) This reverts a change that completely breaks the TTLE and RTM. This is IMPORTANT!**
* Toontown phase files that include all the dna files. [These](https://github.com/open-toontown/resources) work fine.
* Basic knowledge on how streets are setup
* Here you have two options:
    * The advanced option
        * Build yourself a copy of [Disyer's libtoontown](https://github.com/darktohka/libtoontown), and drop the .pyd files in the root directory.
        * Recent Panda3D build (1.10.7 or later) running on *__Python 3__*. This editor is NOT compatible with Python 2.x and will NOT ever be made compatible as Python 2.x is no longer supported.
    * **OR** the easy option:
        * you can download [my copy](https://drive.google.com/file/d/1EbfuG4AaPpeaDKWWeZIxUckFTvYfRQbL/view?usp=sharing) of panda with the compatible libtoontown files in there. Just drag Panda3D-1.11.0-Py37-x64 to your C drive root directory and the libotp.pyd and libtoontown.pyd files to the root level editor directory. Note that the PYD files in here are ONLY compatible with MY copy of panda, so if you are using any other build you have to rebuild them yourself.

~~### You can also pick up a pre-built build in the releases tab~~ *Coming Soon*

## Credits
* [drewcification](https://github.com/drewc5131) - Project Lead | Developer
* [Disyer](https://github.com/darktohka/) - Updating [LIBTOONTOWN](https://github.com/darktohka/libtoontown) to be compatible with modern panda and python 3 | Other Assistance

## Help
* If you encounter a bug, create an issue and attach the .dna file (and any models required). *If this is private information that you do not want to share on this public repo, feel free to send me a DM on discord @drewcification#5131*
    
## Upcoming Features
* Optional Auto PDNA compilation support for [libpandadna](https://github.com/loblao/libpandadna) and Corporate Clash's DNA reader.
* Auto Saving
* and much more!

## Known Incompatibilities
* Corporate Clash's Acorn Acres street buildings (and likely YOTT as well)
    * This is due to the models not being created with the proper node setup. Substitute them with another playground's buildings in the storage dna file. This issue occurs in all released versions of the level editor as well. Ensure your custom buildings are created PROPERLY.

# FAQ
### Why can't I load a street from X playground?
* Make sure the hood's storage file is loaded. You do this by adding it to the `--hoods` launch option. For example, if you want to work on a street in Donald's Dock and another in Minnie's Melodyland, you set the launch option `-hoods DD ML`

### Do I have to credit the use of this editor?
* There is NO requirement to list this editor anywhere in your game credits, but you definitely can do so to spread the word!

### How do I move the camera?
* Move: ALT + Middle Mouse
* Rotate: ALT + Left Mouse
* Zoom: ALT + Right Mouse
* You can also use your number pad or number row to view preset angles
* Note that the camera always moves around the object you have selected

### Some of my props are using textures as if they were in a different playgrond?
* This is OK. This is just because you have support for more than 1 playground loaded. This is only visual in the editor, but I recommend you only load the zone you are working on.

### How do I scale props?
* Select the prop and hold control + left mouse and drag
