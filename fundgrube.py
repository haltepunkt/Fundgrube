from dataclasses import dataclass, fields
from enum import Enum
from requests_cache import CachedSession
from typing import Tuple


class Retailer(Enum):
    MEDIAMARKT = 'MediaMarkt'
    SATURN = 'SATURN'


class Posting:
    def __init__(self,
                 retailer: Retailer,
                 id: str,
                 product_id: int,
                 category_id: str,
                 name: str,
                 text: str,
                 image_urls: list,
                 brand_id: int,
                 brand: str,
                 price: float,
                 price_old: float,
                 discount: int,
                 shipping_cost: float,
                 shipping_type: str,
                 outlet_id: int,
                 outlet: str
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
        self.outlet_id = outlet_id
        self.outlet = outlet

        self.product_url = f'https://www.{retailer.value.lower()}.de/' \
            f'de/product/_-{product_id}.html'

    def thumbnail_url(self, thumbnail_size=200) -> str:
        return f'{self.image_urls[0]}?x={thumbnail_size}&y={thumbnail_size}'

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

    filtered = {
        key: value for key,
        value in arguments.items() if key in field_set
    }

    return class_name(**filtered)


class Fundgrube:
    def __init__(self,
                 retailer: Retailer = Retailer.MEDIAMARKT,
                 cache_expire_after: int = 10
                 ):
        self.user_agent = '{} {}'.format(
            'Fundgrube/1.0',
            '(https://github.com/haltepunkt/Fundgrube)'
        )

        self.retailer = retailer

        self.__session = CachedSession(
            'cache',
            expire_after=cache_expire_after
        )

        self.__base_url = f'https://www.{self.retailer.value.lower()}.de/' \
            'de/data/fundgrube/api/'

    def __postings(self, limit=1, offset=0,
                   outlet_ids=[],
                   category_ids=[],
                   brands=[],
                   search=None
                   ):
        url = f'{self.__base_url}postings?limit={limit}&offset={offset}'

        if len(outlet_ids) > 0:
            outlet_ids_formatted = '%2C'.join(
                [str(outlet_id) for outlet_id in outlet_ids]
            )

            url = url + f'&outletIds={outlet_ids_formatted}'

        if len(brands) > 0:
            url = url + f'&brands={"%2C".join(brands)}'.replace(' ', '+')

        if len(category_ids) > 0:
            url = url + f'&categorieIds={"%2C".join(category_ids)}'

        if search is not None:
            url = url + f'&text={search.replace(" ", "+")}'

        response = self.__session.get(
            url,
            headers={
                'Accept': '*/*',
                'User-Agent': self.user_agent
            }
        )

        if response.status_code == 200:
            postings = response.json()

            more_postings_available = postings.get(
                'morePostingsAvailable',
                False
            )

            return postings, more_postings_available, url

        return {}, False, url

    def postings(self,
                 limit: int = 1,
                 offset: int = 0,
                 outlet_ids: list[int] = [],
                 category_ids: list[str] = [],
                 brands: list[str] = [],
                 search: str = None
                 ) -> Tuple[list[Posting], bool, str]:
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
            except ValueError:
                price = None

            try:
                price_old = float(posting['price_old'])
            except ValueError:
                price_old = None

            product_posting = \
                Posting(
                    retailer=self.retailer,
                    id=posting['posting_id'],
                    product_id=posting['pim_id'],
                    category_id=posting['top_level_catalog_id'],
                    name=posting['name'],
                    text=posting['posting_text'],
                    image_urls=posting['original_url'],
                    brand_id=posting['brand']['id'],
                    brand=posting['brand']['name'],
                    price=price,
                    price_old=price_old,
                    discount=posting['discount_in_percent'],
                    shipping_cost=posting['shipping_cost'],
                    shipping_type=posting['shipping_type'],
                    outlet_id=posting['outlet']['id'],
                    outlet=posting['outlet']['name']
                )

            product_postings.append(product_posting)

        return product_postings, more_postings_available, url

    def categories(self) -> list[Category]:
        postings, _, _ = self.__postings()

        categories = postings.get('categories', [])

        return [to_dataclass(Category, category) for category in categories]

    def brands(self) -> list[Brand]:
        postings, _, _ = self.__postings()

        brands = postings.get('brands', [])

        return [to_dataclass(Brand, brand) for brand in brands]

    def outlets(self) -> list[Outlet]:
        postings, _, _ = self.__postings()

        outlets = postings.get('outlets', [])

        return [to_dataclass(Outlet, outlet) for outlet in outlets]

    def outlet(self, outlet_name) -> Outlet:
        outlets = self.outlets()

        for outlet in outlets:
            if outlet.name == outlet_name:
                return outlet

        return None
