import numpy as np
import pandas as pd
from astropy.time import Time

def day_fraction_to_hms(day_frac):
    hours = int(day_frac * 24)
    minutes = int((day_frac * 24 - hours) * 60)
    seconds = ((day_frac * 24 - hours) * 60 - minutes) * 60
    return hours, minutes, seconds

def build_iso(row):
    y, m = row['year'], row['month']
    d_int = int(row['day'])
    d_frac = row['day'] - d_int
    h, mi, s = day_fraction_to_hms(d_frac)
    return f"{y:04d}-{m:02d}-{d_int:02d}T{h:02d}:{mi:02d}:{s:06.3f}"


def unpack_designation(packed):
    century_map = {'I': 1800, 'J': 1900, 'K': 2000}
    if len(packed) != 7:
        return None
    c = packed[0].upper()
    if c not in century_map:
        return None
    try:
        year = century_map[c] + int(packed[1:3])
    except ValueError:
        return None
    half_month = packed[3].upper()

    fifth = packed[4]
    sixth = packed[5]
    seventh = packed[6]

    try:
        if fifth.isalpha():
            cycle_count = (ord(fifth.upper()) - ord('A') + 1) * 100 + int(sixth)
        else:
            cycle_count = int(fifth) * 10 + int(sixth)
    except ValueError:
        cycle_count = 0

    second_letter = seventh

    if cycle_count > 0:
        return f"{year} {half_month}{second_letter}{cycle_count}"
    else:
        return f"{year} {half_month}{second_letter}"


# Učitaj CSV fajl
df = pd.read_csv("lsst.csv")  # zameni imenom fajla

# Parsiraj packed oznake (pretpostavlja se da su uvek prvih 7 karaktera)


df['packed'] = df['obs80'].str.slice(5, 12)

df['year'] = (df['obs80'].str.slice(15, 19)).astype(int)
df['month'] = (df['obs80'].str.slice(20, 22)).astype(int)
df['day'] = (df['obs80'].str.slice(23, 34)).astype(float)

# Primenimo na DataFrame
df['iso_time'] = df.apply(build_iso, axis=1)

# Pretvori u MJD
df['mjd'] = df['iso_time'].apply(lambda t: Time(t, format='isot', scale='utc').mjd)



df['packed'] = df['obs80'].str.slice(5, 12)
df['mag_val'] = df['obs80'].str.slice(65, 70).str.strip()
df['mag_band'] = df['obs80'].str.slice(70, 71)

# Za svaki jedinstveni asteroid, izdvoji podatke i snimi u fajl
for packed in df['packed'].unique():
    unpacked = (unpack_designation(packed)).replace(' ', '_')
    df_subset = df[df['packed'] == packed][['mjd', 'mag_val', 'mag_band']]
    filename = f"light_curves/{unpacked}.csv"
    df_subset.to_csv(filename, index=False, header=True, sep='\t')


