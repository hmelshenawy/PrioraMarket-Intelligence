import argparse
from  algolia_client import AlgoliaClient
import time
from processor.extractor import ListProcessor

def main():
    parser = argparse.ArgumentParser(description="Dubizzle scraper CLI")
    parser.add_argument("--source", default="dubizzle", help="Marketplace source")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    args = parser.parse_args()

    page= 0
    totalPages=1

    client = AlgoliaClient()
    processor = ListProcessor()
    

    while page <= totalPages:
        response = client.extract("mercedes-benz" , condition="used", page=page, hitsPerPage=20)

        if page==0:
            totalPages = response.get("nbPages")
            print(totalPages)
        page+=1 
        print("----------------------------------current PAge!!", page)
        for hit in response.get("hits"):
         data = processor.getList(hit)
         print("Extract Data:!! ", data)
        time.sleep(3)

if __name__ == "__main__":
    main()