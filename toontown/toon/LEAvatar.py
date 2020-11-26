from otp.avatar import LocalAvatar

class LEAvatar(LocalAvatar.LocalAvatar):
    def __init__(self, cr, chatMgr, chatAssistant, passMessagesThrough = False):
        LocalAvatar.LocalAvatar.__init__(self, cr, chatMgr, chatAssistant, passMessagesThrough)

    def getAutoRun(self):
        return 0
