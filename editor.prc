####################################################

# Use open gl
load-display pandagl

# These control the placement and size of the default rendering window.
win-origin 50 50
win-size 1280 720

# Set engine window title
window-title Open Level Editor - Engine View
icon-filename resources/openttle_ico_temp.ico

# The framebuffer-hardware flag forces it to use an accelerated driver.
framebuffer-hardware #t

# hw animation
hardware-animated-vertices true

# We only want warning info, except for DNA which we spam
notify-level warning
default-directnotify-level warning
notify-level-dna spam

# Model Path
model-path    $MAIN_DIR

# Enable/disable performance profiling tool and frame-rate meter
want-pstats            #f
show-frame-rate-meter  #t
frame-rate-meter-update-interval 0.01

# Enable audio using the FMOD audio library by default:
audio-library-name p3fmod_audio

# Enable the model-cache, but only for models, not textures.
model-cache-dir $USER_APPDATA/ToontownLevelEditor/cache
model-cache-textures #f

# Default Extensions
default-model-extension .bam
screenshot-extension png