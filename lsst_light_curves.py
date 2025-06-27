import pandas as pd
from astropy.time import Time
import numpy as np
from astroquery.jplhorizons import Horizons
import time

from astropy.coordinates import SkyCoord, get_sun, EarthLocation, solar_system_ephemeris, get_body_barycentric
import astropy.units as u


def phase_angle(epoch, designation):
    # Heliocentrična pozicija asteroida
    asteroid_hc = Horizons(id=designation, location='500@10', epochs=epoch).vectors()
    asteroid_hc = np.array([asteroid_hc['x'], asteroid_hc['y'], asteroid_hc['z']])  # shape (3, N)

    # Geocentrična pozicija asteroida
    asteroid_gc = Horizons(id=designation, location='399', epochs=epoch).vectors()
    asteroid_gc = np.array([asteroid_gc['x'], asteroid_gc['y'], asteroid_gc['z']])  # shape (3, N)

    # Norme po vektorima (kolonama)
    r_hc = np.linalg.norm(asteroid_hc, axis=0)
    r_gc = np.linalg.norm(asteroid_gc, axis=0)

    # Jedinični vektori
    asteroid_hc_unit = asteroid_hc / r_hc
    asteroid_gc_unit = asteroid_gc / r_gc

    # Skalarni proizvod između -r_hc i -r_gc
    cos_alpha = np.einsum('ij,ij->j', -asteroid_hc_unit, -asteroid_gc_unit)  # shape (N,)

    alpha_rad = np.arccos(np.clip(cos_alpha, -1, 1))
    alpha_deg = np.degrees(alpha_rad)

    return alpha_deg, r_hc, r_gc



df = pd.read_csv("lsst.csv")  # zameni imenom fajla

# Ukloni " UTC" iz stringova (ako postoji)
df['obstime_clean'] = df['obstime'].str.replace(' UTC', '', regex=False)


ra = df['ra']
dec = df['dec']

# Napravi praznu kolonu za MJD
df['mjd'] = None
df['phase angle'] = None
df['r_hc'] = None
df['r_gc'] = None


unique_provids = df['provid'].unique()

batch_size = 50
br = 0
for prov in unique_provids:
    print(f'{prov}, {br} out of {len(unique_provids)}')
    mask = df['provid'] == prov
    times = df.loc[mask, 'obstime_clean'].values

    mjds = np.zeros(len(times))
    jds = np.zeros(len(times))

    try:
        for i in range(len(times)):
            t = Time(times[i], format='iso', scale='utc')
            mjds[i] = t.mjd
            jds[i] = t.jd

        sort_idx = np.argsort(jds)
        jds_sorted = jds[sort_idx]

        # Prazne liste za rezultate
        alpha_sorted, r_hc_sorted, r_gc_sorted = [], [], []

        # Podeli u segmente
        for i in range(0, len(jds_sorted), batch_size):
            batch = jds_sorted[i:i + batch_size]

            alpha_batch, r_hc_batch, r_gc_batch = phase_angle(batch, prov)

            alpha_sorted.extend(alpha_batch)
            r_hc_sorted.extend(r_hc_batch)
            r_gc_sorted.extend(r_gc_batch)

        # Vrati rezultate u originalni redosled
        unsort_idx = np.argsort(sort_idx)
        alpha = np.array(alpha_sorted)[unsort_idx]
        r_hc = np.array(r_hc_sorted)[unsort_idx]
        r_gc = np.array(r_gc_sorted)[unsort_idx]

        # Zapiši u DataFrame
        df.loc[mask, 'mjd'] = mjds
        df.loc[mask, 'phase angle'] = alpha
        df.loc[mask, 'r_hc'] = r_hc
        df.loc[mask, 'r_gc'] = r_gc

    except Exception as e:
        msg = f'Greška za object {prov}: {e}'
        print(msg)
        with open('greske.log', 'a') as fajl:
            fajl.write(msg + '\n')
        
        df.loc[mask, ['mjd', 'phase angle', 'r_hc', 'r_gc']] = None

    br = br + 1
    time.sleep(0.5)
    
    if np.mod(br, 50) == 0:
        time.sleep(10)
        print('cekamo 10 sekundi')








# =============================================================================
# # Petlja kroz redove i konvertuj po jedan datum
# for i, dt_str in enumerate(df['obstime_clean']):
#     
#     if np.mod(i, 10)==0:
#         print(f'{i} out of {len(df["obstime_clean"])}')
#         
#     try:
#         t = Time(dt_str, format='iso', scale='utc')
#         
#         
#         alpha_deg, r_hc, r_gc = phase_angle(t.jd, df['provid'][i])
#         
#         df.at[i, 'mjd'] = t.mjd
#         df.at[i, 'phase angle'] = alpha_deg
#         df.at[i, 'r_hc'] = r_hc
#         df.at[i, 'r_gc'] = r_gc
#         
#         
#         
#     except Exception as e:
#         print(f"Greška na redu {i}: {dt_str} -> {e}")
#         df.at[i, 'mjd'] = None
# =============================================================================
        
        

        
#for i in range(len(ra)):   
#    
#    if np.mod(i, 100)==0:
#        print(i)
#    t = Time(df['mjd'][i], format='mjd')  
#    with solar_system_ephemeris.set('jpl'):
#        sun_pos = get_body_barycentric('sun', t)
#    with solar_system_ephemeris.set('jpl'):
#        earth_pos = get_body_barycentric('earth', t)
#        
#    # Vektor Zemlja -> Sunce
#    vec_earth_to_sun = sun_pos.xyz - earth_pos.xyz
#    vec_earth_to_sun = vec_earth_to_sun / np.linalg.norm(vec_earth_to_sun)
#    
#    # Vektor Zemlja -> asteroid iz RA/Dec, jedinicni vektor
#    asteroid_dir = SkyCoord(ra=ra[i]*u.deg, dec=dec[i]*u.deg, distance=1*u.AU, frame='icrs')
#    vec_earth_to_ast = asteroid_dir.cartesian.xyz
#    vec_earth_to_ast = vec_earth_to_ast / np.linalg.norm(vec_earth_to_ast)
#    
#    
#    vec_sun_to_ast = vec_earth_to_ast - vec_earth_to_sun
#    vec_sun_to_ast = vec_sun_to_ast / np.linalg.norm(vec_sun_to_ast)
#    
#    # Izracunaj ugao iz skalar product
#    cos_alpha = np.dot(vec_earth_to_ast.value, vec_sun_to_ast.value)
#    alpha_rad = np.arccos(np.clip(cos_alpha, -1, 1))
#    alpha_deg = np.degrees(alpha_rad)
#    
#    df.at[i, 'phase angle'] = alpha_deg
        

# Za svaki jedinstveni asteroid, izdvoji podatke i snimi u fajl
for provid in df['provid'].unique():
      
    df_subset = df[df['provid'] == provid][['mjd', 'phase angle', 'r_hc', 'r_gc', 'mag', 'rmsmag', 'band']]
    df_subset = df_subset.sort_values(by='mjd')  # sortiranje po mjd rastuće
    filename = f"light_curves/{provid.replace(' ', '_')}.csv"
    df_subset.to_csv(filename, index=False, header=True, sep='\t')


