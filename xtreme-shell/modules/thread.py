from threading import Thread as t


class Thread(t):
    unfinished_threads = []

    def __init__(self, function, *args, **kwargs):
        super().__init__()

        self.func = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            (th := Thread(func, *args, **kwargs)).start()
            return th

        return wrapper

    def run(self):
        Thread.unfinished_threads.append(self)
        self.func(*self.args, **self.kwargs)
        Thread.unfinished_threads.remove(self)
