import pandas as pd
from astropy.time import Time
import numpy as np

from astropy.coordinates import SkyCoord, get_sun, EarthLocation, solar_system_ephemeris, get_body_barycentric
import astropy.units as u


df = pd.read_csv("lsst.csv")  # zameni imenom fajla

# Ukloni " UTC" iz stringova (ako postoji)
df['obstime_clean'] = df['obstime'].str.replace(' UTC', '', regex=False)


ra = df['ra']
dec = df['dec']

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
        
        
#df['phase angle'] = None
#        
for i in range(len(ra[:1])):   
    
    if np.mod(i, 100)==0:
        print(i)
    t = Time(df['mjd'][i], format='mjd')  
    with solar_system_ephemeris.set('jpl'):
        sun_pos = get_body_barycentric('sun', t)
    with solar_system_ephemeris.set('jpl'):
        earth_pos = get_body_barycentric('earth', t)
        
    # Vektor Zemlja -> Sunce
    vec_earth_to_sun = sun_pos.xyz - earth_pos.xyz
    vec_earth_to_sun = vec_earth_to_sun / np.linalg.norm(vec_earth_to_sun)
    
    # Vektor Zemlja -> asteroid iz RA/Dec, jedinicni vektor
    asteroid_dir = SkyCoord(ra=ra[i]*u.deg, dec=dec[i]*u.deg, distance=1*u.AU, frame='icrs')
    vec_earth_to_ast = asteroid_dir.cartesian.xyz
    vec_earth_to_ast = vec_earth_to_ast / np.linalg.norm(vec_earth_to_ast)
    
    
    vec_sun_to_ast = vec_earth_to_ast - vec_earth_to_sun
    vec_sun_to_ast = vec_sun_to_ast / np.linalg.norm(vec_sun_to_ast)
    
    # Izracunaj ugao iz skalar product
    cos_alpha = np.dot(vec_earth_to_ast.value, vec_sun_to_ast.value)
    alpha_rad = np.arccos(np.clip(cos_alpha, -1, 1))
    alpha_deg = np.degrees(alpha_rad)
    
#    df.at[i, 'phase angle'] = alpha_deg
        