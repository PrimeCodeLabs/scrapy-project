class ManageStrategiesUseCase:
    def __init__(self, repository):
        self.repository = repository

    def add_strategy(self, strategy):
        return self.repository.insert_strategy(strategy)

    def get_strategies(self):
        return self.repository.get_strategies()

    def get_strategy(self, website):
        return self.repository.get_strategy(website)

    def delete_strategy(self, website):
        return self.repository.delete_strategy(website)
