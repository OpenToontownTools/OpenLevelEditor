# Toontown Open Level Editor
 
## An open sourced modernized version of Disney's in-house Toontown Online level editor used to create .dna files.

## Requirements
### ***IMPORTANT***
* **You need a Panda3D build with [THIS](https://github.com/drewc5131/panda3d/commit/2b735df2d0b8f9880311a9a08a28c7ec684e9583) fix (You can just edit the .py file in ur SDK) This reverts a change that completely breaks the TTLE and RTM. This is IMPORTANT!**
* Build yourself a copy of [Disyer's libtoontown](https://github.com/darktohka/libtoontown), and drop the .pyd files in the root directory.
* Recent Panda3D build running on *__Python 3__*. This editor is NOT compatible with Python 2.x and will NOT ever be made compatible as Python 2.x is no longer supported.

~~### You can also pick up a pre-built build in the releases tab~~ *Coming Soon, however you can grab my build of panda3d and compatible builds of lib toontown with it HERE. you MUST use that panda build if you use the pyd files in that zip.*


## Credits
* [drewcification](https://github.com/drewc5131) - Project Lead | Developer
* [Disyer](https://github.com/darktohka/) - Updating [LIBTOONTOWN](https://github.com/darktohka/libtoontown) to be compatible with modern panda and python 3 | Other Assistance

## Help
* If you encounter a bug, create an issue and attach the .dna file (and any models required). *If this is private information that you do not want to share on this public repo, feel free to send me a DM on discord @drewcification#5131*

## Known Incompatibilities
* Corporate Clash's Acorn Acres street buildings (and likely YOTT as well)
    * This is due to the models not being created with the proper node setup. Substitute them with another playground's buildings in the storage dna file. This issue occurs in all released versions of the level editor as well. Ensure your custom buildings are created PROPERLY.
