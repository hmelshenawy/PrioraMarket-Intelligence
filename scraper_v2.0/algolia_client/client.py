from algolia_client.base_client import BaseAlgoliaClient 
from config import KEYS
import requests


class AlgoliaClient():
    def __init__(self):

        self.algolia_url = KEYS.ALGOLIA_URL2
        self.app_id = KEYS.ALGOLIA_APP_ID
        self.api = KEYS.ALGOLIA_API_KEY
        self.algolia_header = {
                        "X-Algolia-Application-Id": self.app_id,
                        "X-Algolia-API-Key": self.api,
                        "Content-Type": "application/json",
                    }
        print("Header Created!! ", self.algolia_header)


    def extract(self, make: str,condition: str, page: int, hitsPerPage: int):
        header = self.algolia_header
        url = self.algolia_url
        query = self.makeQuery( self.makeFilter(condition=condition,make= make),page, hitsPerPage)
        session = requests.session()
        response= session.post(
            url= url,
            headers=header,
            json= query
            
        )
        # print(response.json())
        return response.json()


    def makeFilter(self, condition: str , make: str ):
        filter = f'"category_v2.slug_paths\":\"motors/{condition}-cars/{make}"'

        return filter

    def makeQuery(self, filter: str, page, hitsPerPage):
        query = {
  "query": "",
  "filters": filter,
  "hitsPerPage": hitsPerPage,
  "page": page,
  "attributesToRetrieve": [
   "objectID",
  "id",
  "uuid",
  "name",
  "price",
  "year",
  "kilometers",
  "details",
  "category_v2",
  "seller_type",
  "places"
  ],
  "attributesToHighlight": []
}
        return query