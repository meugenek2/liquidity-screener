


#! standard imports
import os
import time
import json
import numpy as np
import pandas as pd
import requests


class MarketScreener():
	KEY = "1348b4e9d6c429f964f1ad2436b552a2788d88e2efaa501bca7350b761f4" #! defipulse api key
	def __init__(self, refresh=False):
		if not os.path.exists("data"):
			os.makedirs("data")
		if not os.path.exists("screened"):
			os.makedirs("screened")
		if refresh:
			self.data = self.get_data()
		self.data = self.load_data()
	def load_data(self):
		files = [file for file in [f for f in os.listdir("data") if os.path.isfile(os.path.join("data", f))] if ".json" in file]
		latest_timestamp = max([int(f.split("_")[0]) for f in files])
		with open("data/{e}_coingecko.json".format(e=latest_timestamp)) as jfile:
			data = json.load(jfile)
		return data
	def get_data(self):
		defipulse_data = {}
		defipulse = "https://data-api.defipulse.com/api/v1/defipulse/api/"
		response = requests.get(defipulse + "GetProjects", params={"api-key": self.KEY}).json()
		for item in response:
			name = item["name"].lower()
			defipulse_data[name] = item["value"]["tvl"]["USD"]["value"]
		coingecko_data = []
		coingecko = "https://api.coingecko.com/api/v3/"
		for page in range(1,11):
			payload = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 250, "page": page}
			response = requests.get(coingecko + "coins/markets", params=payload).json()
			for item in response:
				name = item["name"].lower()
				if name in defipulse_data:
					item["tvl"] = defipulse_data[name]
				item["ticker"] = item["symbol"].upper()
				coingecko_data.append(item)
		with open("data/{e}_coingecko.json".format(e=int(1000.*time.time())), "w") as jfile:
			json.dump(coingecko_data, jfile)
		return coingecko_data
	def screen(self, volume=1000000., market_cap=100000000., tvl=100000000.):
		df = pd.DataFrame(self.data)
		df["volume"] = df["total_volume"]
		df["price"] = df["current_price"]
		df = df[["name", "ticker", "price", "volume", "market_cap", "circulating_supply", "tvl"]]
		mask = (df["volume"] > volume) & (df["market_cap"] > market_cap) & ((df["tvl"] > tvl) | df["tvl"].isna())
		df = df[mask]
		df.to_csv("screened/{e}.csv".format(e=int(1000.*time.time())))



if __name__ == "__main__":


	x = MarketScreener(refresh=False)
	x.screen(volume=1000000., market_cap=100000000., tvl=100000000.)



