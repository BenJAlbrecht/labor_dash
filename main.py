import pandas as pd
from load_BLS.load_bls import read_bls

# Testing
url = "https://download.bls.gov/pub/time.series/la/la.data.1.CurrentS"
df = read_bls(url)

print(df.head(5))