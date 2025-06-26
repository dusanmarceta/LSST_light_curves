import pandas as pd
from astropy.time import Time

df = pd.read_csv("lsst.csv")  # zameni imenom fajla

# Ukloni " UTC" iz stringova (ako postoji)
df['obstime_clean'] = df['obstime'].str.replace(' UTC', '', regex=False)

# Napravi praznu kolonu za MJD
df['mjd'] = None

# Petlja kroz redove i konvertuj po jedan datum
for i, dt_str in enumerate(df['obstime_clean']):
    try:
        t = Time(dt_str, format='iso', scale='utc')
        df.at[i, 'mjd'] = t.mjd
    except Exception as e:
        print(f"Greška na redu {i}: {dt_str} -> {e}")
        df.at[i, 'mjd'] = None

# Za svaki jedinstveni asteroid, izdvoji podatke i snimi u fajl
for provid in df['provid'].unique():
    
    df_subset = df[df['provid'] == provid][['mjd', 'mag', 'rmsmag', 'band']]
    df_subset = df_subset.sort_values(by='mjd')  # sortiranje po mjd rastuće
    filename = f"light_curves/{provid.replace(' ', '_')}.csv"
    df_subset.to_csv(filename, index=False, header=True, sep='\t')


