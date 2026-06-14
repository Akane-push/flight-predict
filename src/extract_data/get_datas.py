import sys
import os
from datetime import datetime
from src.extract_data.flight_data import LufthansaFly
from src.extract_data.weather_data import Weather
from src.tools.data_cleaning import DataCleaning as cl

from dotenv import load_dotenv
load_dotenv()
datas_path = os.getenv("EXTRACTED_PATH")

filename_flight = "_flightdatas.parquet"
filename_weather = "_weatherdatas.parquet"
filename_fids = "_FIDS.parquet"

class GetDatas:
    """
    Class Scheduler
    Outputs:
        - get_flights(self, time: str) : extract flight data for a given date and save it in a parquet file
        - get_weather(self) : extract weather data for a given date and save it in a parquet file
        - get_scheduled_flights(self, time: str, PARAM: str, IATA: str) : (In progress)
    """
    
    def __init__(self, date: str):
        """
        date = 'AAAA-MM-DD'
        """
        import polars as pl
        self.pl = pl
        self.date = date

    # Generate the files for flight  ================================================
    def get_flights(self, time: str):
        """
        time = 'HH:MM'
        """
        date_time = self.date + "T" + time
        self.df_flight_list = LufthansaFly(date_time).extract_flights()

        if self.df_flight_list.is_empty():
            print("[INFO] No available datas")
            return

        name_data_file = self.date + filename_flight
        file_path = os.path.join(datas_path, name_data_file)

        if os.path.exists(file_path):
            df_existant = self.pl.read_parquet(file_path)
            df_final = self.pl.concat([df_existant, self.df_flight_list], how="vertical")
            df_final.write_parquet(file_path)
            print(f"[INFO] Datas are added in the: {file_path} file !")

        else:
            self.df_flight_list.write_parquet(file_path)
            print(f"[INFO] Datas are available in the: {file_path} file !")

    # Generate the files for scheduled flights  ================================================
    def get_scheduled_flights(self, time: str, PARAM: str, IATA: str):
        """
        time = 'HH:MM'
        """
        date_time = self.date + "T" + time
        self.df_flights = LufthansaFly(date_time).extract_scheduled_flights(PARAM, IATA)

        if self.df_flights.is_empty():
            print("[INFO] No available datas")
            return

        df_weather = Weather().extract_scheduled_weather(self.date, PARAM, IATA)
        
        df_clean = cl().get_cleaned(df_flights, df_weather)

        name_data_file = PARAM + "_" + IATA + "_" + self.date + filename_fids
        file_path = os.path.join(datas_path, name_data_file)

        if os.path.exists(file_path):
            df_existant = self.pl.read_parquet(file_path)
            df_final = self.pl.concat([df_existant, self.df_clean], how="vertical")
            df_final = df_final.unique(subset=["Flight_Number"], keep="last")
            df_final.write_parquet(file_path)
            print(f"[INFO] Datas are added in the: {file_path} file !")

        else:
            self.df_clean.write_parquet(file_path)
            print(f"[INFO] Datas are available in the: {file_path} file !")

    # Generate the file for weather  ================================================
    def get_weather(self):
        self.df_weather = Weather().extract_weather(self.date)
        self.save_weather()

    def save_weather(self):
        if self.df_weather is None:
            print("[WARNING] Can't generate weather file")
            return
            
        name_data_file = self.date + filename_weather
        file_path = os.path.join(datas_path, name_data_file)

        self.df_weather.write_parquet(file_path)
        print(f"[INFO] Datas are available in the: {file_path} file !")
    

if __name__ == "__main__":
    GetDatas("2026-04-04").get_flights("15:00")
    GetDatas("2026-04-04").get_archive_weather()