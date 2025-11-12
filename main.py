import os
from typing import Dict
import httpx
from mcp.server.fastmcp import FastMCP
import json
import logging

# Initialise FastMCP Server
mcp = FastMCP("fewsnet")

# constants
API_BASE_URL = 'https://fdw.fews.net/api'
AUTH_ENDPOINT = 'https://fdw.fews.net/api-token-auth/'


def get_config() -> Dict[str, str]:
    return {
        "username": os.environ.get("username", ""),
        "password": os.environ.get("password", "")
    }


def get_token() -> str:
    data = get_config()
    with httpx.AsyncClient() as client:
        response = client.post(AUTH_ENDPOINT, data=data, timeout=30.0)
        response.raise_for_status()
        return response.json()['token']


def get_headers() -> Dict[str, str]:
    token = get_token()
    return {
        "Authorization": f"JWT {token}"
    }


def make_request(url: str, country_code: str, start_date: str) -> str:
    params = {
        "country_code": country_code,
        "start_date": start_date
    }
    headers = get_headers()

    with httpx.AsyncClient() as client:
        try:
            response = client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            logging.debug(response.json())
            text = response.text
            logging.info(text)
            return text
        except Exception:
            return json.dumps({"error": "request failed"})


@mcp.tool(
    name="get_market_price_facts",
    description="get time series market prices for specific products from hte United Nations Central Product "
                "Classification")
def get_market_price_facts(country_code: str, start_date: str) -> str:

    url = f"{API_BASE_URL}/marketpricefacts"
    return make_request(url=url, country_code=country_code, start_date=start_date)


@mcp.tool(
    name="get_cross_border_trade",
    description="get cross border trade time series data for specific products from hte United Nations Central Product "
                "Classification")
def get_cross_border_trade(country_code: str, start_date: str) -> str:

    url = f"{API_BASE_URL}/tradeflowquantityvalue"
    return make_request(url=url, country_code=country_code, start_date=start_date)


@mcp.tool(
    name="get_fews_net_food_security_classification",
    description="Classification and series catalog data"
)
def get_fews_net_food_security_classification(country_code: str, start_date: str) -> str:

    url = f"{API_BASE_URL}/ipcclassification"
    return make_request(url=url, country_code=country_code, start_date=start_date)


@mcp.tool(
    name="get_food_insecure_population_estimates",
    description="get data on food insecure population estimates"
)
def get_food_insecure_population_estimates(country_code: str, start_date: str) -> str:

    url = f"{API_BASE_URL}/ipcpopulation"
    return make_request(url=url, country_code=country_code, start_date=start_date)


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
