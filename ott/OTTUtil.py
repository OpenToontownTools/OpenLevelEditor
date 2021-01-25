"""
Helpers and such for Open Toontown Tools
"""
from direct.task.TaskManagerGlobal import taskMgr


def sleep(duration: float):
    """
    Breaks for a number of seconds. Returns an awaitable.
    @LittleToonCat

    :param duration: Duration of sleep
    """

    def __task(task):
        if task.time > duration:
            return task.done
        return task.cont

    return taskMgr.add(__task)
