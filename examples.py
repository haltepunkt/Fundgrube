from fundgrube import *
import pprint

pp = pprint.PrettyPrinter()

fundgrube = Fundgrube(retailer=Retailer.MEDIAMARKT)

# Categories, including counts of postings
pp.pprint(fundgrube.categories())

# Brands, including counts of postings
pp.pprint(fundgrube.brands()[:4])

# Outlets, including counts of postings
pp.pprint(fundgrube.outlets()[:4])

# Postings by category
postings, _, _ = fundgrube.postings(limit=4, category_ids=['CAT_DE_MM_115', 'CAT_DE_MM_8000'])
pp.pprint(postings)

# Postings by brand
postings, _, url = fundgrube.postings(limit=4, brands=['APPLE', 'CASIO'])
pp.pprint(url)
pp.pprint(postings)

# Outlet by name, followed by postings by outlet
outlet = fundgrube.outlet(outlet_name='Bonn')

if outlet is not None:
  pp.pprint(outlet)

  postings, _, _ = fundgrube.postings(limit=4, outlet_ids=[outlet])
  pp.pprint(postings)

# Text search
postings, _, _ = fundgrube.postings(limit=4, search='iPhone SE')
pp.pprint(postings)
