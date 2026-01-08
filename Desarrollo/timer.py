import time

class Timer:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.elapsed = 0

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed += int(time.time() - self.start_time)
            self.running = False

    def reset(self):
        self.elapsed = 0
        self.running = False

    def get_elapsed(self):
        if self.running:
            return self.elapsed + int(time.time() - self.start_time)
        return self.elapsed
