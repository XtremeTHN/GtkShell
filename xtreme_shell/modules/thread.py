import threading


class Thread(threading.Thread):
    unfinished_threads = []

    def __init__(self, function, *args, **kwargs):
        super().__init__()

        self.func = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        (th := Thread(self.func, *args, **kwargs)).start()
        return th

    def run(self):
        Thread.unfinished_threads.append(self)
        self.func(*self.args, **self.kwargs)
        Thread.unfinished_threads.remove(self)
