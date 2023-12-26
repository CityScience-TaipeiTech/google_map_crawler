import json
import re
import requests
from bs4 import BeautifulSoup as Soup
import csv
from time import sleep


def extract_link(atag: str) -> str:
    html_string = atag

    pattern = r'href="([^"]*)"'

    matches = re.findall(pattern, html_string)

    if matches:
        url = matches[0]
        return url
    else:
        print("No match for extract_link()")


def curl_gmap_address(url: str) -> str:
    html_content = requests.get(url).text

    soup = Soup(html_content, "html.parser")

    try:
        addr = (
            soup.find_all("meta", property="og:site_name")[0]
            .get("content")
            .split("·")[1]
        )

        return addr

    except:
        print("exception in curl_gmap_address()")


def extract_lat_lon(html_str: str):
    lat_lon_re = r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"

    matches = re.findall(lat_lon_re, html_str)

    if matches:
        lat, lon = matches[0]
        return (lat, lon)
    else:
        print("No latitude and longitude found in the string.")


def list_to_json_file(ls: list, filename: str) -> None:
    with open(filename, "a") as f:
        json.dump(ls, f)


def main():
    # placename, address, lat, lon, type
    time = 0
    lis = []
    with open("parking_test.json") as f:
        data = json.load(f)

    for d in data:
        if len(data[d]) == 0:
            continue

        ele = data[d]

        for e in ele:
            tmp = {}

            (lat, lon) = extract_lat_lon(e["a"])
            link = extract_link(e["a"])
            addr = curl_gmap_address(link)

            if not addr:
                continue

            tmp["place_name"] = e["div"]
            tmp["address"] = addr
            tmp["lat"] = lat
            tmp["lon"] = lon
            tmp["type"] = e["type"]

            lis.append(tmp)

            print(str(time) + str(addr))
            time += 1

            with open("parking_test_processed.json", "w") as f:
                json.dump(lis, f)

            with open("parking_memo_processed.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([e["div"]])

            if time % 10 == 0:
                print("sleeping ...")
                sleep(3)

    # list_to_json_file(lis, "parking_test_processed.json")


if __name__ == "__main__":
    main()
