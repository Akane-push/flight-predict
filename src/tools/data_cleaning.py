import polars as pl
import polars.selectors as cs
from joblib import load

pl.Config.set_tbl_cols(26)

class DataCleaning():
    def cleaning(self, df_flight : pl.DataFrame, df_weather : pl.DataFrame):
        '''
        Must include both flight and weather DataFrames (polars format)
        '''
        df_flight = df_flight.unique()
        df_flight = df_flight.drop_nulls()

        df_weather = df_weather.unique()
        df_weather = df_weather.with_columns(pl.col("Date").dt.date().alias("Date"))

        df_flight = self.merge_datetime(df_flight, "Dep_Actual_Date", "Dep_Actual_Time", "Dep_Actual_DateTime")
        df_flight = self.merge_datetime(df_flight, "Dep_Scheduled_Date", "Dep_Scheduled_Time", "Dep_Scheduled_DateTime")
        df_flight = self.merge_datetime(df_flight, "Arr_Actual_Date", "Arr_Actual_Time", "Arr_Actual_DateTime")
        df_flight = self.merge_datetime(df_flight, "Arr_Scheduled_Date", "Arr_Scheduled_Time", "Arr_Scheduled_DateTime")
        df_weather = self.merge_datetime(df_weather, "Date", "Time", "DateTime")

        df_flight = df_flight.with_columns((pl.col("Arr_Scheduled_DateTime") - pl.col("Dep_Scheduled_DateTime")).alias("Flight_Duration"))
        df_flight = df_flight.with_columns(((pl.col("Dep_Actual_DateTime") - pl.col("Dep_Scheduled_DateTime")).dt.total_seconds() // 60).alias("Dep_Delay"))
        df_flight = df_flight.with_columns(((pl.col("Arr_Actual_DateTime") - pl.col("Arr_Scheduled_DateTime")).dt.total_seconds() // 60).alias("Arr_Delay"))

        df_flight = df_flight.with_columns(pl.when(pl.col("Arr_Delay") > 0).then(1).otherwise(0).alias("Delay"))
        
        df_weather = df_weather.sort(["IATA", "DateTime"])
        df_flight = df_flight.sort(["Departure_IATA", "Dep_Actual_DateTime"])
        self.df_final = df_flight.join_asof(df_weather, left_on="Dep_Actual_DateTime", right_on="DateTime", by_left="Departure_IATA", by_right="IATA", strategy="forward", suffix="_Dep")
        df_flight = df_flight.sort(["Arrival_IATA", "Arr_Scheduled_DateTime"])
        self.df_final = self.df_final.join_asof(df_weather, left_on="Arr_Scheduled_DateTime", right_on="DateTime", by_left="Arrival_IATA", by_right="IATA", strategy="forward", suffix="_Arr")

        self.df_final = self.df_final.drop(["DateTime", "DateTime_Arr", "Dep_Actual_DateTime", "Dep_Scheduled_DateTime",
                                            "Arr_Actual_DateTime", "Arr_Scheduled_DateTime", "Arr_Delay"])
        self.df_final = self.df_final.drop_nulls(subset=["Temperature_2m", "Wind_Speed_100m", "Wind_Direction_100m",
                                                         "Surface_Pressure", "Weather_Code", "Precipitation", "Temperature_2m_Arr",
                                                         "Wind_Speed_100m_Arr", "Wind_Direction_100m_Arr", "Surface_Pressure_Arr",
                                                         "Weather_Code_Arr", "Precipitation_Arr"])
        self.replacement_weather()


    def merge_datetime(self, df : pl.DataFrame, date_col, time_col , output_name : str):
        df = df.with_columns(
            pl.format("{} {}", pl.col(date_col), pl.col(time_col))
            .str.to_datetime("%Y-%m-%d %H:%M")
            .alias(output_name)
                              )
        df = df.drop(date_col, time_col)
        return df
    

    def replacement_weather(self) :
        replacement_weather_dict = {"0": "clear",
                                    "1": "clear", "2": "clear",
                                    "3": "cloudy",
                                    "45": "fog", "48": "fog",
                                    "51": "fog",
                                    "53": "drizzle", "55": "drizzle",
                                    "56": "drizzle", "57": "drizzle",
                                    "61": "rain", "63": "rain", "65": "rain",
                                    "66": "rain", "67": "rain",
                                    "71": "snow", "73": "snow", "75": "snow",
                                    "77": "snow",
                                    "80": "showers", "81": "showers", "82": "showers",
                                    "85": "showers", "86": "showers",
                                    "95": "thunderstorm",
                                    "96": "thunderstorm", "99": "thunderstorm"}
        
        self.df_final = self.df_final.with_columns([pl.col("Weather_Code").cast(pl.String).replace(replacement_weather_dict).alias("Weather_Description"),
                                                    pl.col("Weather_Code_Arr").cast(pl.String).replace(replacement_weather_dict).alias("Weather_Description_Arr")])


    def encoding(self) :
        ordinal_encoder = load('../Machine_Learning/oe.joblib') #Ajouter gestion chemin en fonction du service
        ordinal_encoder.set_output(transform="polars")

        numerical_cols = self.df_final.select(cs.numeric()).columns
        categorical_cols = self.df_final.select(cs.string()).columns

        df_cat_encoded = ordinal_encoder.transform(self.df_final.select(categorical_cols))
        
        #self.df_final = self.df_final.drop(["Flight_Number"])
        self.encoded_df = pl.concat([self.df_final.select(numerical_cols), df_cat_encoded], how="horizontal").select(sorted(self.df_final.columns))
        

    def get_encoded(self, df_clean : pl.DataFrame) :
        self.df_final = df_clean
        self.encoding()
        return self.encoded_df
    
    def get_cleaned(self, df_flight : pl.DataFrame, df_weather : pl.DataFrame) :
        self.cleaning(df_flight, df_weather)
        return self.df_final
    
    def get_cleaned_encoded(self, df_flight : pl.DataFrame, df_weather : pl.DataFrame) :
        self.cleaning(df_flight, df_weather)
        self.encoding()
        return self.df_final