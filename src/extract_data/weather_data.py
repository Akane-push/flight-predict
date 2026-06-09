import openmeteo_requests
import polars as pl
import sys
import os
from dotenv import load_dotenv
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

#Loading required files
current_folder = os.path.dirname(__file__)
path = os.path.join(current_folder, "..", "reference_data", "airports_references.parquet")
df_IATA_refs = pl.read_parquet(path)

from dotenv import load_dotenv
load_dotenv()
datas_path = os.getenv("EXTRACTED_PATH")
pending_path = os.getenv("PENDING_PATH")

filename_flight = "_flightdatas.parquet"

#Open-Meteo config
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

class Weather:
    #Load datas from Open-Meteo API
    def extract_weather(self, date: str):
        """
        date = 'AAAA-MM-DD'
        """
        self.date = date

        datas_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        threshold_date = datetime.now().date() - timedelta(days=4)

        if datas_date <= threshold_date:
            self.url = "https://archive-api.open-meteo.com/v1/archive"
        else :
            self.url = "https://api.open-meteo.com/v1/forecast"

        return self.openmeteo_extract()
    

    def extract_scheduled_weather(self, df_flights: pl.DataFrame):
        df_IATA = pl.concat([df_flights['Departure_IATA'], df_flights['Arrival_IATA']])
        self.liste_IATA = df_IATA.unique().to_list()

        self.url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.df_IATA_l_L['Latitude'].to_list(),
            "longitude": self.df_IATA_l_L['Longitude'].to_list(),
            "hourly": ["temperature_2m", "wind_speed_100m", "wind_direction_100m", "surface_pressure", "weather_code", "precipitation", "wind_gusts_10m", "wind_direction_10m", "wind_speed_10m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high"],
            "timezone": "auto",
            "forecast_days": 1,
            "past_days": 1,
        }
        self.responses = openmeteo.weather_api(self.url, params = params)
        
        return self.openmeteo_separate()
    

    def openmeteo_extract(self):
        if self.load_datas() is None:
            return None

        params = {
            "latitude": self.df_IATA_l_L['Latitude'].to_list(),
            "longitude": self.df_IATA_l_L['Longitude'].to_list(),
            "start_date": (datetime.strptime(self.date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d"),
            "end_date": self.date,
            "hourly": ["temperature_2m", "wind_speed_100m", "wind_direction_100m", "surface_pressure", "weather_code", "precipitation", "wind_gusts_10m", "wind_direction_10m", "wind_speed_10m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high"],
            "timezone": "auto",
        }
        self.responses = openmeteo.weather_api(self.url, params = params)
        
        return self.openmeteo_separate()

    #Load flight data file
    def load_datas(self):
        self.file_name = self.date + filename_flight
        self.file_path = os.path.join(datas_path, self.file_name)
        return self.loading_datas()


    #Extract IATA list, longitude and latitude
    def loading_datas(self):
        if os.path.exists(self.file_path):
            self.df_flight_list = pl.read_parquet(self.file_path)
            df_IATA = pl.concat([self.df_flight_list['Departure_IATA'], self.df_flight_list['Arrival_IATA']])
            self.liste_IATA = df_IATA.unique().to_list()
        
        else:
            print(f"[WARNING] No {self.file_name} file existing")
            return None

        self.df_IATA_l_L = df_IATA_refs.filter(pl.col("Airport_IATA").is_in(self.liste_IATA))
        self.df_IATA_l_L = self.df_IATA_l_L.drop(self.df_IATA_l_L.columns[:3])
        return self.df_IATA_l_L



    #Transform Open-Meteo data into a data frame
    def openmeteo_separate(self):
        self.hourly_df = pl.DataFrame()
        for i in range(len(self.responses)):
            response = self.responses[i]
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_wind_speed_100m = hourly.Variables(1).ValuesAsNumpy()
            hourly_wind_direction_100m = hourly.Variables(2).ValuesAsNumpy()
            hourly_surface_pressure = hourly.Variables(3).ValuesAsNumpy()
            hourly_weather_code = hourly.Variables(4).ValuesAsNumpy()
            hourly_precipitation = hourly.Variables(5).ValuesAsNumpy()

            hourly_data = {"date": pl.datetime_range(
                    start = datetime.fromtimestamp(hourly.Time() + response.UtcOffsetSeconds()),
                    end = datetime.fromtimestamp(hourly.TimeEnd() + response.UtcOffsetSeconds()),
                    interval = f"{hourly.Interval()}s",
                    closed = "left",
                    eager = True)}

            hourly_data["IATA"] = self.liste_IATA[i]
            hourly_data["Temperature_2m"] = hourly_temperature_2m
            hourly_data["Wind_Speed_100m"] = hourly_wind_speed_100m
            hourly_data["Wind_Direction_100m"] = hourly_wind_direction_100m
            hourly_data["Surface_Pressure"] = hourly_surface_pressure
            hourly_data["Weather_Code"] = hourly_weather_code
            hourly_data["Precipitation"] = hourly_precipitation
            
            hourly_data = pl.DataFrame(data = hourly_data)
            dates_list = hourly_data["date"].dt.date().to_list()
            hours_list = hourly_data["date"].dt.strftime("%H:%M").to_list()
            hourly_data = hourly_data.drop("date")
            hourly_data.insert_column(1, pl.Series("Date", dates_list))
            hourly_data.insert_column(2, pl.Series("Time", hours_list))

            self.hourly_df = pl.concat([self.hourly_df, hourly_data])
        return self.hourly_df



if __name__ == "__main__":
    print(Weather("2026-03-30").extract_current_weather().head())