import threading
import subprocess


def PopenAndCall(onExit, *popenArgs, **popenKWArgs):
    def runInThread(onExit, popenArgs, popenKWArgs):
        proc = subprocess.Popen(*popenArgs, **popenKWArgs)
        # with stop handle
        while proc.poll() is None:
            if thread.stopped():
                proc.kill()
                break
        onExit()
        return

    thread = StoppableThread(target=runInThread, args=(onExit, popenArgs, popenKWArgs))
    thread.start()
    return thread


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
