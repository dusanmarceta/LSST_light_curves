from astroquery.jplhorizons import Horizons
import numpy as np
# Horizons traži Julian Date, npr. 2460480.5 je 26. jun 2025


asteroid_hc = Horizons(id='2025 MW22', location='500@10', epochs=np.array([2460754., 2460756.]))
asteroid_hc = asteroid_hc.vectors()
sun_ac =  -np.array([asteroid_hc['x'][:], asteroid_hc['y'][:], asteroid_hc['z'][:]])


asteroid_gc = Horizons(id='2025 MW22', location='399', epochs=2460754.)
asteroid_gc = asteroid_gc.vectors()
earth_ac =  np.array([asteroid_gc['x'][0], asteroid_gc['y'][0], asteroid_gc['z'][0]])


sun_ac = sun_ac / np.linalg.norm(sun_ac)
earth_ac = earth_ac / np.linalg.norm(earth_ac)

cos_alpha = np.dot(sun_ac, earth_ac)
alpha_rad = np.arccos(np.clip(cos_alpha, -1, 1))
alpha_deg = np.degrees(alpha_rad)



def phase_angle(epoch, designation):
    asteroid_hc = Horizons(id=designation, location='500@10', epochs=epoch)
    asteroid_hc = asteroid_hc.vectors()
    sun_ac =  -np.array([asteroid_hc['x'][0], asteroid_hc['y'][0], asteroid_hc['z'][0]])
    
    
    
    
    asteroid_gc = Horizons(id=designation, location='399', epochs=epoch)
    asteroid_gc = asteroid_gc.vectors()
    earth_ac =  np.array([asteroid_gc['x'][0], asteroid_gc['y'][0], asteroid_gc['z'][0]])
    
    r_hc = np.linalg.norm(sun_ac)
    r_gc = np.linalg.norm(earth_ac)
    
    sun_ac = sun_ac / r_hc
    earth_ac = earth_ac / r_gc
    
    cos_alpha = np.dot(sun_ac, earth_ac)
    alpha_rad = np.arccos(np.clip(cos_alpha, -1, 1))
    alpha_deg = np.degrees(alpha_rad)
    
    return (alpha_deg, r_hc, r_gc)





