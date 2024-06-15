import pandas as pd

class DataCleaningService:
    def clean_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        df.dropna(inplace=True)
        df['content'] = df['content'].str.lower()
        return df.to_dict(orient='records')
