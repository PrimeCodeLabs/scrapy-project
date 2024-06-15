class StrategyService:
    def __init__(self, manage_strategies_use_case):
        self.manage_strategies_use_case = manage_strategies_use_case

    def add_strategy(self, strategy):
        return self.manage_strategies_use_case.insert_strategy(strategy)

    def get_strategies(self):
        return self.manage_strategies_use_case.get_strategies()

    def get_strategy(self, website):
        return self.manage_strategies_use_case.get_strategy(website)

    def delete_strategy(self, website):
        return self.manage_strategies_use_case.delete_strategy(website)
