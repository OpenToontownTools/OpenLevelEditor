'''
Helpers and such for Open Toontown Tools
'''

def sleep(duration):
    '''
    Breaks for a number of seconds. Returns an awaitable.
    @LittleToonCat
    '''
    def __task(task):
        if task.time > duration:
            return task.done
        return task.cont

   return taskMgr.add(__task)
