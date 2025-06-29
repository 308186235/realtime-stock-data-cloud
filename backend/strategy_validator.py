# 新增蒙特卡洛验证类
class MonteCarloValidator:
    def __init__(self, iterations=1000):
        self.iterations = iterations
        
    def validate_strategy(self, strategy):
        results = []
        for _ in range(self.iterations):
            simulated_data = self._generate_market_data()
            results.append(strategy.execute(simulated_data))
        return self._analyze_results(results)
