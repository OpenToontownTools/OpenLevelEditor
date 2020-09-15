####################################################

# Use open gl
load-display pandagl

# These control the placement and size of the default rendering window.

win-origin 50 50
win-size 1280 720

# The framebuffer-hardware flag forces it to use an accelerated driver.
framebuffer-hardware #t

# Use 4x msaa
framebuffer-multisample #t
multisamples 4

# We want some more debugging info, but not too much
notify-level info
default-directnotify-level info

# Model Path
model-path    $MAIN_DIR

## This enable the automatic creation of a TK window when running
## Direct.
#
#want-directtools  #f
#want-tk           #f

# Enable/disable performance profiling tool and frame-rate meter

want-pstats            #f
show-frame-rate-meter  #t

# Enable audio using the FMOD audio library by default:
audio-library-name p3fmod_audio


# Enable the model-cache, but only for models, not textures.
model-cache-dir $USER_APPDATA/ToontownLevelEditor/cache
model-cache-textures #f

# Default Extensions
default-model-extension .bam
screenshot-extension png