# services/metrics_manager.py

class MetricsManager:
    def __init__(self):
        self.metrics = {}

    def increment(self, name, value=1):
        if name not in self.metrics:
            self.metrics[name] = 0
        self.metrics[name] += value

    def get_metric(self, name):
        return self.metrics.get(name, 0)

    def get_all_metrics(self):
        return self.metrics
