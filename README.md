# Fundgrube

Search remaining stock, floor models, customer returns, etc. of MediaMarkt and SATURN.

## Usage

```
from fundgrube import *

fundgrube = Fundgrube(retailer=Retailer.MEDIAMARKT)

postings, more_postings_available = fundgrube.postings()
```

See [examples.py](https://github.com/haltepunkt/Fundgrube/blob/master/examples.py) for further usage expamples.
