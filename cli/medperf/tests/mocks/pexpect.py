class MockChild:
    def __init__(self, exitstatus):
        self.exitstatus = exitstatus

    def isalive(self):
        return False

    def close(self):
        pass


class MockPexpect:
    def __init__(self, exitstatus):
        self.exitstatus = exitstatus

    def spawn(self, command: str, timeout: int = 30) -> MockChild:
        return MockChild(self.exitstatus)

