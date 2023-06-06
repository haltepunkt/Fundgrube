# Fundgrube

Search remaining stock, floor models, customer returns, etc. of [MediaMarkt](https://www.mediamarkt.de/de/data/fundgrube) and [SATURN](https://www.saturn.de/de/data/fundgrube).

## Usage

```
from fundgrube import *

fundgrube = Fundgrube(retailer=Retailer.MEDIAMARKT)

postings, more_postings_available = fundgrube.postings()
```

See [examples.py](https://github.com/haltepunkt/Fundgrube/blob/master/examples.py), or [example_discounts.py](https://github.com/haltepunkt/Fundgrube/blob/master/example_discounts.py) for further usage examples.
