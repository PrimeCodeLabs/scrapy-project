class ExtractDataUseCase:
    def __init__(self, repository, data_cleaning_service):
        self.repository = repository
        self.data_cleaning_service = data_cleaning_service

    def extract_and_clean_data(self, criteria):
        raw_data = self.repository.get_data(criteria)
        cleaned_data = self.data_cleaning_service.clean_data(raw_data)
        return cleaned_data
