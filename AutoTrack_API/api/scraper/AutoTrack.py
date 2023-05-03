from concurrent.futures import ThreadPoolExecutor
from scrapy import Selector
import requests
import json


http_proxy = "http://ibrahimmalik:oMAULCCWkk0ezF2t_country-UnitedStates@proxy.packetstream.io:31112"
https_proxy = "http://ibrahimmalik:oMAULCCWkk0ezF2t_country-UnitedStates@proxy.packetstream.io:31112"

proxyDict = {
    "http": http_proxy,
    "https": https_proxy,
}

URL = "https://search.autotrack.nl/api/v1/listings/search-with-counters?pageNumber={}&pageSize=90&sortField=relevance&sortOrder=desc&abTest=A"

headers = {
    "accept": "application/json, text/plain, */*",
    "authorization": "Basic YXBwczo2U21Oa1dSRmJCdGM=",
    "content-type": "application/json",
    "origin": "https://www.autotrack.nl",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

def get_all_ids():
    r = requests.get("http://127.0.0.1:8000/api/get_car_ids/", headers={"User-Agent": headers.get("User-Agent")})
    return json.loads(r.content)

class Scraper:

    def __init__(self):
        self.all_ids = get_all_ids()
        self.cmp = []
        self.new_ads = []
        self.added_cars = []
        self.count = 0

    def save_data(self, data_dict):
        requests.post(
            "http://127.0.0.1:8000/api/add_car", headers={"content-type": "application/json", "User-Agent": headers.get("User-Agent")}, json=data_dict)
        self.added_cars.append(data_dict.get("car_id"))
        print(f"Saved -----------------> {len(self.added_cars)}")

    def add_new_products(self):
        json_resp = self.get_listings_response(1)
        total_pages = list(range(round(json_resp.get("total")/json_resp.get("pageSize"))+1))
        array_of_arrays = [total_pages[i:i+200] for i in range(0, len(total_pages), 200)]
        for item in array_of_arrays:
            with ThreadPoolExecutor() as executor:
                executor.map(self.get_new_ids, item)
        with ThreadPoolExecutor() as executor:
            executor.map(self.get_data, self.new_ads)
        with ThreadPoolExecutor() as executor:
            executor.map(self.save_data, [item for item in self.cmp if item.get("car_id") not in self.added_cars])

        
    def get_new_ids(self, page_number):
        json_resp = self.get_listings_response(page_number)
        for item in json_resp.get("hits"):
            ad_id = item.get("advertentieId")
            if ad_id not in self.all_ids:
                ad_url = item.get("url")
                self.new_ads.append(ad_url)

    def adding_all_products(self):
        pg = 1
        json_resp = self.get_listings_response(pg)
        total_pages = round(json_resp.get("total")/json_resp.get("pageSize"))
        while True:
            print(f"Scraping Page # {pg}")
            links = self.get_listings(json_resp)
            with ThreadPoolExecutor() as executor:
                executor.map(self.get_data, links)
            with ThreadPoolExecutor() as executor:
                executor.map(self.save_data, [item for item in self.cmp if item.get("car_id") not in self.added_cars])
            if pg < total_pages:
                pg += 1
                json_resp = self.get_listings_response(pg)
            else:
                break
        print("Completed!")

    @staticmethod
    def get_listings_response(page):
        while True:
            try:
                r = requests.post(URL.format(page), headers=headers, json={}, proxies=proxyDict)
                return json.loads(r.content)
            except:
                pass

    def get_listings(self, json_resp):
        cmp = []
        for item in json_resp.get("hits"):
            if item.get("advertentieId") not in self.all_ids:
                cmp.append(item.get("url"))
        return cmp

    @staticmethod
    def get_response(link):
        r = requests.get(link, headers={"User-Agent": headers.get("User-Agent")}, proxies=proxyDict)
        return Selector(text=r.content)

    def get_data(self, link):
        response = self.get_response(link)
        json_data = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        json_resp = json.loads(json_data)
        data = json_resp.get("props").get("initialProps").get("pageProps").get("data")
        ad_id = data.get("advertentieId")
        title = "".join(response.xpath("//h1[contains(@class, 'title')]//text()").getall()).strip()
        subtitle = " ".join(response.xpath("//h2[contains(@class, 'subtitle')]//text()").getall()).strip()
        price = "".join(response.xpath("(//span[contains(@class, 'PriceTag__') and .//b])[last()]//text()").getall()).strip()
        year = " ".join(response.xpath("//span[contains(@class, 'year')]//text()").getall()).strip()
        mileage = " ".join(response.xpath("//span[contains(@class, 'mileage')]//text()").getall()).strip()
        seller_data = data.get("aanbieder").get("aanbiedergegevens")
        seller_name = seller_data.get("naam")
        seller_city = seller_data.get("plaatsnaam")
        postal_code = seller_data.get("postcode")
        st_ad = seller_data.get("straatnaam")
        h_nmbr = seller_data.get("huisnummer")
        tel = seller_data.get("telefoonnummer")
        website = seller_data.get("website")
        car_images = data.get("autogegevens").get("algemeen").get("fotoUrls")
        fnl = {
            "seller": {
                "name": seller_name,
                "city": seller_city,
                "zip": postal_code,
                "street_ad": st_ad,
                "house_number": h_nmbr,
                "phone": tel,
                "web": website
            },
            "general": {
                "title": title,
                "subtitle": subtitle,
                "price": price,
                "year": year,
                "mileage": mileage,
                "images": car_images
            },
            "overview": []
        }
        for item in response.xpath("//ul[@data-testid='mileageTestId']/li"):
            label = " ".join(item.xpath(".//span[contains(@class, 'label')]//text()").getall()).strip()
            value = " ".join(item.xpath(".//text()[not(parent::span[contains(@class, 'label')])]").getall()).strip()
            fnl.get("overview").append({
                "label": label,
                "value": value
            })
        fnl["options"] = []
        for item in data.get("opties"):
            op_name = item.get("naam")
            op_values = [itm.get("naam") for itm in item.get("opties")]
            fnl.get("options").append({
                "name": op_name,
                "values": op_values
            })
        fnl["specs"] = []
        for item in response.xpath("//section[contains(@data-observer-name, 'Specificaties')]//div[./button[@data-testid]]"):
            spec_name = " ".join(item.xpath(".//button//text()").getall()).strip()
            data_dict = {
                "heading": spec_name,
                "specs": []
            }
            for itm in item.xpath(".//div[contains(@class, 'ParseSpecifications__Table')]/div"):
                name = " ".join(itm.xpath("./div[1]//text()").getall()).strip()
                value = " ".join(itm.xpath("./div[2]//text()").getall()).strip()
                if "|" in value:
                    value = value.split("|")[0].strip()
                data_dict.get("specs").append({
                    "name": name,
                    "value": value
                })
            fnl.get("specs").append(data_dict)
        self.cmp.append({
            "car_id": ad_id,
            "car_data": fnl
        })
        self.count += 1
        print(f"Scraped -----------------> {self.count}")

s = Scraper()
s.adding_all_products()