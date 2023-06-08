from dataclasses import dataclass, fields
from enum import Enum
from requests_cache import CachedSession

class Retailer(Enum):
  MEDIAMARKT = 'MediaMarkt'
  SATURN = 'SATURN'

class Posting:
  def __init__(self,
    retailer,
    id, product_id, category_id,
    name, text, image_urls,
    brand_id, brand,
    price, price_old, discount,
    shipping_cost, shipping_type,
    thumbnail_size=200
  ):
    self.retailer = retailer.value

    self.id = id
    self.product_id = product_id
    self.category_id = category_id

    self.name = name
    self.text = text
    self.image_urls = image_urls

    self.brand_id = brand_id
    self.brand = brand

    self.price = price
    self.price_old = price_old
    self.discount = discount

    self.shipping_cost = shipping_cost
    self.shipping_type = shipping_type

    self.thumbnail_url = f'{image_urls[0]}?x={thumbnail_size}&y={thumbnail_size}'
    self.product_url = f'https://www.{retailer.value.lower()}.de/de/product/_-{product_id}.html'

  def __repr__(self):
    return f'{self.__class__}: {self.__dict__}'

@dataclass
class Object:
  id: int
  name: str
  count: int

@dataclass
class Category(Object):
  pass

@dataclass
class Brand(Object):
  pass

@dataclass
class Outlet(Object):
  pass

def to_dataclass(class_name, arguments):
  field_set = {field.name for field in fields(class_name) if field.init}

  filtered = {key: value for key, value in arguments.items() if key in field_set}

  return class_name(**filtered)

# Fundgrube API
class Fundgrube:
  def __init__(self, retailer=Retailer.MEDIAMARKT, cache_expire_after=10):
    self.retailer = retailer

    self.__session = CachedSession('cache', expire_after=cache_expire_after)
    self.__base_url = f'https://www.{self.retailer.value.lower()}.de/de/data/fundgrube/api/'

  def __postings(self, limit=1, offset=0, outlet_ids=[], category_ids=[], brands=[], search=None):
    url = f'{self.__base_url}postings?limit={limit}&offset={offset}'

    if len(outlet_ids) > 0:
      url = url + f'&outletIds={"%2C".join([str(outlet_id) for outlet_id in outlet_ids])}'

    if len(brands) > 0:
      url = url + f'&brands={"%2C".join(brands)}'.replace(' ', '+')

    if len(category_ids) > 0:
      url = url + f'&categorieIds={"%2C".join(category_ids)}'

    if search is not None:
      url = url + f'&text={search.replace(" ", "+")}'

    response = self.__session.get(url, headers={
      'Accept' : '*/*',
      'User-Agent': 'Fundgrube/1.0 (https://github.com/haltepunkt/Fundgrube)'
    })

    if response.status_code == 200:
      postings = response.json()

      more_postings_available = postings.get('morePostingsAvailable', False)

      return postings, more_postings_available, url

    return {}, False, url

  def postings(self, limit=1, offset=0, outlet_ids=[], category_ids=[], brands=[], search=None):
    if limit > 99:
      limit = 99

    postings, more_postings_available, url = self.__postings(
      limit=limit,
      offset=offset,
      outlet_ids=outlet_ids,
      category_ids=category_ids,
      brands=brands,
      search=search
    )

    product_postings = []

    for posting in postings.get('postings', []):
      try:
        price = float(posting['price'])
      except:
        price = None

      try:
        price_old = float(posting['price_old'])
      except:
        price_old = None

      product_posting = Posting(
        retailer=self.retailer,
        id=posting['posting_id'], product_id=posting['pim_id'], category_id=posting['top_level_catalog_id'],
        name=posting['name'], text=posting['posting_text'], image_urls=posting['original_url'],
        brand_id=posting['brand']['id'], brand=posting['brand']['name'],
        price=price, price_old=price_old, discount=posting['discount_in_percent'],
        shipping_cost=posting['shipping_cost'], shipping_type=posting['shipping_type'],
      )

      product_postings.append(product_posting)

    return product_postings, more_postings_available, url

  def categories(self):
    postings, _, _ = self.__postings()

    categories = postings.get('categories', [])

    return [to_dataclass(Category, category) for category in categories]

  def brands(self):
    postings, _, _ = self.__postings()

    brands = postings.get('brands', [])

    return [to_dataclass(Brand, brand) for brand in brands]

  def outlets(self):
    postings, _, _ = self.__postings()

    outlets = postings.get('outlets', [])

    return [to_dataclass(Outlet, outlet) for outlet in outlets]

  def outlet(self, outlet_name):
    outlets = self.outlets()

    for outlet in outlets:
      if outlet.name == outlet_name:
        return outlet

    return None
