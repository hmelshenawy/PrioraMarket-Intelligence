import re

class ListProcessor():
    def __init__(self):
        self.getList = self.getList

    def getList(self, hit :dict):

        details = hit.get("details", {})

        car_details = {
                    "id": hit.get("id"),
        "uuid": hit.get("uuid"),
        "price": hit.get("price"),
        "year": hit.get("year"),
        "kilometers": hit.get("kilometers"),
        "seller_type": normalize_text(hit.get("seller_type")),
        "name": hit.get("name", {}).get("en"),
        "location": hit.get("places", {}).get("en", []),
        "make": normalize_text(get_detail_value(details, "Make")),
        "model": normalize_text(get_detail_value(details, "Model")),
        "trim": normalize_text(get_detail_value(details, "Trim")),
        "fuel_type": normalize_text(get_detail_value(details, "Fuel Type")),
        "transmission": normalize_text(get_detail_value(details, "Transmission Type")),
        "body_type": normalize_text(get_detail_value(details, "Body Type")),
        "exterior_color": normalize_text(get_detail_value(details, "Exterior Color")),
        "horsepower": get_detail_value(details, "Horsepower"),

        }
        return car_details


def get_detail_value(details: dict, key: str, lang: str = "en"):
    """يجيب قيمة حقل من details بأمان، حتى لو الحقل ناقص"""
    return details.get(key, {}).get(lang, {}).get("value")

def normalize_text(value: str):

    value = value.strip()
    
    value = re.sub(r"[-_\s]+", "", value)  # يشيل كل الشرطات والمسافات (كل حاجة مع بعض في نمط واحد)

    
    # يشيل أي مسافات زيادة بعد الاستبدال
    value = re.sub(r"\s+", " ", value).strip()
    
    return value.lower()