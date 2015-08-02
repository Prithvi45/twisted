from threading import Lock, local as LocalStorage
from ._threadworker import LockWorker
from ._team import Team


@classmethod
def pool(currentLimit, threadFactory=None):
    """
    Construct a L{Team} that spawns threads as a thread pool, with the given
    limiting function.

    @param withLimit: a callable that returns the current limit on the number
        of workers that the returned L{Team} should create; if it already has
        more workers than that value, no new workers will be created.
    @type withLimit: 0-argument callable returning L{int}

    @param reactor: If passed, the L{IReactorFromThreads} / L{IReactorCore} to
        be used to coordinate actions on the L{Team} itself.  Otherwise, a
        L{LockWorker} will be used.

    @return: a new L{Team}.
    """
    try:
        from Queue import Queue
    except ImportError:
        from queue import Queue

    from ._threadworker import ThreadWorker

    from twisted.python.log import err
    if threadFactory is None:
        from threading import Thread as threadFactory
    def startThread(target):
        return threadFactory(target=target).start()
    def limitedWorkerCreator():
        stats = team.statistics()
        if stats.busyWorkerCount + stats.idleWorkerCount >= currentLimit():
            return None
        return ThreadWorker(startThread, Queue())

    coordinator = LockWorker(Lock(), LocalStorage())

    team = Team(coordinator=coordinator,
                createWorker=limitedWorkerCreator,
                logException=err)
    return team


