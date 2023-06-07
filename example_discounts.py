from fundgrube import *
import time

search = 'APPLE'

fundgrube_mediamarkt = Fundgrube(retailer=Retailer.MEDIAMARKT, cache_expire_after=60)
fundgrube_saturn = Fundgrube(retailer=Retailer.SATURN, cache_expire_after=60)

postings = []
more_postings_available_mediamarkt = True
more_postings_available_saturn = True

limit = 99
offset = 0
api_call_count = 0

while more_postings_available_mediamarkt or more_postings_available_saturn:
  postings_mediamarkt, more_postings_available_mediamarkt = fundgrube_mediamarkt.postings(limit=limit, offset=offset, search=search)
  postings_saturn, more_postings_available_saturn = fundgrube_saturn.postings(limit=limit, offset=offset, search=search)

  postings.extend(postings_mediamarkt)
  postings.extend(postings_saturn)

  offset += limit
  api_call_count += 1

  if api_call_count % 4 == 0:
    time.sleep(2)

print(f'Postings fetched: {len(postings)}')

for discount in [50, 60, 70, 80, 90]:
  print(f'Discount of {discount}% or higher: {sum(posting.discount >= discount for posting in postings)}')

for price in [10, 5]:
  print(f'Price of {price}€ or lower: {sum(posting.price <= price for posting in postings)}')

for posting in sorted(postings, key=lambda posting: posting.discount):
  if posting.discount >= 50 or posting.price <= 5:
    print(f'{posting.product_id} | {posting.discount:>2}% | {posting.retailer:<10} | {posting.brand} {posting.name} ({posting.price_old}€ -> {posting.price}€)')
