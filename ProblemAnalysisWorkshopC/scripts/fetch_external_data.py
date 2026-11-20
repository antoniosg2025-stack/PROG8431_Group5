"""Download the two external sources used in Workshop C (run once; the results are already in data/).

1. Statistics Canada - Census Profile 2021, census subdivisions (municipalities) of Ontario,
   through the Census Profile SDMX API: https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/
2. Wikidata - inception date (property P571) of each Ontario census subdivision (property P3012 = StatCan code),
   through the Wikidata Query Service: https://query.wikidata.org/

Usage (from the ProblemAnalysisWorkshopC folder):
    python scripts/fetch_external_data.py
"""
import io
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

SDMX_BASE = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/"
OUTPUT_DIR = Path("data")

# Census Profile characteristic id -> (column name, statistic: 1 = count/value, 4 = rate/percentage)
CENSUS_CHARACTERISTICS = {
    1: ("population_2021", 1), 3: ("population_change_pct_2016_2021", 1), 4: ("private_dwellings", 1),
    6: ("population_density_per_km2", 1), 7: ("land_area_km2", 1), 39: ("average_age", 1), 40: ("median_age", 1),
    42: ("pct_single_detached", 4), 43: ("pct_semi_detached", 4), 44: ("pct_row_house", 4),
    47: ("pct_apartment_5plus_storeys", 4), 56: ("average_household_size", 1),
    229: ("median_household_income", 1), 230: ("median_after_tax_household_income", 1),
    238: ("average_household_income", 1), 331: ("pct_low_income_lim_at", 1),
    1401: ("pct_owner_households", 4), 1402: ("pct_renter_households", 4), 1419: ("average_rooms_per_dwelling", 1),
    1427: ("pct_built_1960_or_before", 4), 1472: ("median_monthly_owner_shelter_cost", 1),
    1474: ("median_dwelling_value", 1), 1480: ("median_monthly_rent", 1), 1515: ("pct_immigrants", 4),
    1670: ("pct_visible_minority", 4), 2008: ("pct_bachelor_or_higher", 4), 2228: ("participation_rate", 1),
    2229: ("employment_rate", 1), 2230: ("unemployment_rate", 1), 2604: ("pct_commute_by_car", 4),
    2607: ("pct_commute_by_transit", 4),
}


def ontario_census_subdivisions():
    """Return {SDMX geography code: municipality name} for every Ontario census subdivision."""
    xml_text = requests.get(SDMX_BASE + "codelist/STC_CP/CL_GEO_CSD/latest", timeout=120).text
    namespace = {"s": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
                 "c": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"}
    codes = {}
    for code in ET.fromstring(xml_text).iter("{%s}Code" % namespace["s"]):
        geo = code.get("id")
        name = [n.text for n in code.findall("c:Name", namespace)
                if n.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"]
        if geo.startswith("2021A000535"):
            codes[geo] = name[0] if name else ""
    return codes


def fetch_census(geo_codes, chunk_size=60):
    """Download the selected characteristics for all Ontario census subdivisions (wide table)."""
    characteristic_key = "+".join(str(c) for c in CENSUS_CHARACTERISTICS)
    frames = []
    geo_list = list(geo_codes)
    for start in range(0, len(geo_list), chunk_size):
        geo_key = "+".join(geo_list[start:start + chunk_size])
        url = f"{SDMX_BASE}data/STC_CP,DF_CSD/A5.{geo_key}.1.{characteristic_key}.?format=csv"
        frames.append(pd.read_csv(io.StringIO(requests.get(url, timeout=300).text)))
    long = pd.concat(frames)
    rows = []
    for char_id, (column, statistic) in CENSUS_CHARACTERISTICS.items():
        part = long[(long["CHARACTERISTIC"] == char_id) & (long["STATISTIC"] == statistic)]
        rows.append(part.set_index("REF_AREA")["OBS_VALUE"].rename(column))
    wide = pd.concat(rows, axis=1).reset_index().rename(columns={"REF_AREA": "geo"})
    wide.insert(0, "csd_code", wide["geo"].str[-7:].astype(int))
    wide.insert(1, "csd_name", wide["geo"].map(geo_codes))
    return wide.drop(columns="geo")


def fetch_inception_dates():
    """Inception date (Wikidata P571) for every Ontario census subdivision (Wikidata P3012)."""
    query = """SELECT ?code ?inception WHERE { ?item wdt:P3012 ?code .
               FILTER(STRSTARTS(?code, "35") && STRLEN(?code) = 7) ?item wdt:P571 ?inception }"""
    response = requests.get("https://query.wikidata.org/sparql", params={"query": query, "format": "json"},
                            headers={"User-Agent": "PROG8431-Group5-Workshop-C"}, timeout=120)
    records = [(int(b["code"]["value"]), b["inception"]["value"][:10]) for b in response.json()["results"]["bindings"]]
    dates = pd.DataFrame(records, columns=["csd_code", "municipality_inception_date"]).drop_duplicates("csd_code")
    dates["date_source"] = "Wikidata P571 (inception)"
    return dates


if __name__ == "__main__":
    geographies = ontario_census_subdivisions()
    fetch_census(geographies).to_csv(OUTPUT_DIR / "census_2021_csd_ontario_full.csv", index=False)
    fetch_inception_dates().to_csv(OUTPUT_DIR / "municipality_inception_dates_wikidata.csv", index=False)
    print("Saved the full downloads with the suffixes _full / _wikidata (the notebook uses the curated files).")
