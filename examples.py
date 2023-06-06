from fundgrube import *
import pprint

pp = pprint.PrettyPrinter()

fundgrube = Fundgrube(retailer=Retailer.MEDIAMARKT)

pp.pprint(fundgrube.categories())

pp.pprint(fundgrube.brands()[:4])

outlets = fundgrube.outlets()
pp.pprint(outlets[:4])

postings, _ = fundgrube.postings(limit=4, category_ids=['CAT_DE_MM_115', 'CAT_DE_MM_8000'])
pp.pprint(postings)

postings, _ = fundgrube.postings(limit=4, brands=['APPLE', 'CASIO'])
pp.pprint(postings)

outlet = fundgrube.outlet(outlet_name='Bonn')

if outlet is not None:
  pp.pprint(outlet)

  postings, _ = fundgrube.postings(limit=4, outlet_ids=[outlet])
  pp.pprint(postings)

postings, _ = fundgrube.postings(limit=4, search='iPhone SE')
pp.pprint(postings)
