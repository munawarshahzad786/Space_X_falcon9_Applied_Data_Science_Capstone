# API Reference

Overview

This document lists all APIs used in the Falcon 9 Project, including endpoints, parameters, and usage examples.

1. SpaceX Launch API

Base URL: https://api.spacexdata.com/v5/launches

Endpoints:

GET /latest – Fetch latest Falcon 9 launch

GET /past – Fetch all past launches

GET /upcoming – Fetch upcoming launches

Example (Python):

import requests

url = "https://api.spacexdata.com/v5/launches/latest"
response = requests.get(url)
data = response.json()
print(data)


Response Fields:

name – Mission name

date_utc – Launch date in UTC

rocket – Rocket ID

success – Launch success (True/False)

details – Launch description