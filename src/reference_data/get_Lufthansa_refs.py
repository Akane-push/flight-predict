import sys
import os
import time
import requests
import polars as pl
from src.tools.identification import LufthansaAPI

current_folder = os.path.dirname(__file__)
datas_ref_path = os.path.join(current_folder, "..", "reference_data")
wanted_items = 20000 # nb airports to fetch (default 10500 for all)
#pd.set_option('display.max_rows', wanted_items)
#pd.set_option('display.max_columns', 10)
#pd.set_option('display.max_colwidth', None)

class LufthansaRefs:
    def __init__(self):
        self.api = LufthansaAPI()
        if self.api.token is None:
            self.token = self.api.get_token()
        else:
            self.token = self.api.token
        self.headers = {'Authorization': f'Bearer {self.token}'}

    # Airport import  ================================================
    def get_airports(self):
        url = f"{self.api.url}/mds-references/airports"
        airports_df = pl.DataFrame()
        for i in range(wanted_items // 100):
            data_airports_json = requests.get(f"{url}/?lang=UK&limit=100&offset={i*100}&LHoperated=0", headers=self.headers).json().get('AirportResource', {}).get('Airports', {}).get('Airport', []) # Get data airport
            temp_df = pl.DataFrame({
                                        'Airport_IATA': [code.get("AirportCode") for code in data_airports_json],
                                        'Airport_Name': [name.get("Names",{}).get("Name",{}).get("$") for name in data_airports_json],
                                        'Country_Code': [country.get("CountryCode") for country in data_airports_json],
                                        'Latitude': [item.get("Position",{}).get("Coordinate",{}).get("Latitude") for item in data_airports_json],
                                        'Longitude': [item.get("Position",{}).get("Coordinate",{}).get("Longitude") for item in data_airports_json]
                                    })
            airports_df = pl.concat([airports_df, temp_df])
            time.sleep(5)
        airports_df.set_index('Airport_IATA', inplace=True)
        return airports_df
    
    # Country Name  ================================================
    def get_countries(self):
        url = f"{self.api.url}/mds-references/countries"
        countries_df = pl.DataFrame()
        for i in range(3): 
            data_countries_json = requests.get(f"{url}/?lang=UK&limit=100&offset={i*100}", headers=self.headers).json().get('CountryResource', {}).get('Countries', {}).get('Country', []) # Get data country
            temp_df = pl.DataFrame({
                                        'Country_Code': [code.get("CountryCode") for code in data_countries_json],
                                        'Country_Name': [name.get("Names",{}).get("Name",{}).get("$") for name in data_countries_json]
                                    })
            countries_df = pl.concat([countries_df, temp_df])
            time.sleep(5)
        countries_df.set_index('Country_Code', inplace=True)
        return countries_df

    def waiting_calculation(self):
        outpout ="[INFO] You will waiting for approximatively"
        waiting_s = round((wanted_items / 100) * 5)
        if waiting_s < 60:
            print(f"{outpout} {waiting_s}s")
        else:
            waiting = round(waiting_s / 60 , 0)
            print(f"{outpout} {waiting}m")

    # Get all datas and merge them in a csv file  ================================================
    def get_ref_datas(self):
        name_parquet = "airports_references.parquet"
        file_path = os.path.join(self.datas_ref_path, name_parquet)
        airports_df = self.get_airports()
        time.sleep(5)
        countries_df = self.get_countries()
        refs_df = airports_df.merge(countries_df, left_on="Country_Code", right_index=True, how="inner")
        refs_df = refs_df.reset_index()
        refs_df = refs_df[['Airport_IATA', 'Airport_Name', 'Country_Code', 'Country_Name', 'Latitude', 'Longitude']]
        refs_df.set_index('Airport_IATA', inplace=True)
        refs_df.to_parquet(file_path, engine="pyarrow",  index=True)
        print(f"[INFO] The references are available in the: {name_parquet} file !")       



if __name__ == "__main__":
    LufthansaRefs().waiting_calculation()
    LufthansaRefs().get_ref_datas()