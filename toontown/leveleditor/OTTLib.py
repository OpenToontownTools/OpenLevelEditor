'''
General Open Toontown Tools convenience library
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