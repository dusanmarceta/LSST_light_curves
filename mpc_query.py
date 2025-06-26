#import requests
#
#response = requests.get("https://data.minorplanetcenter.net/api/obscodes", json={"obscode": "X05"})
#
#if response.ok:
#    for key, value in response.json().items():
#        print(f'{key:<27}: {value}')
#else:
#    print("Error: ", response.status_code, response.content)


#with open("UnnObs.txt", "r") as f_in, open("X05_observations.txt", "w") as f_out:
#    for line in f_in:
#        if line.strip().endswith("X05"):
#            f_out.write(line)
#            
            

#import gzip
#
##broj_lsst = 0
##with gzip.open("UnnObs.txt.gz", "rt") as f_in, open("X05_observations.txt", "w") as f_out:
##    for line in f_in:
##
##        if line.strip().endswith("X05"):
##            broj_lsst = broj_lsst + 1
##            print(broj_lsst)
##            
##            f_out.write(line)
#            
#
#with gzip.open("UnnObs.txt.gz", "rt") as f:
#    for line in f:
#        parts = line.strip().split()
#        if len(parts) >= 1:
#            desig = parts[0]
#            if desig.upper().startswith("2025"):
#                designations.add(desig)
#
#print(f"Nađeno {len(designations)} objekata sa oznakom '2025'")
#for d in sorted(designations):
#    print(d)
   
import gzip

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

def extract_designations_starting_with_2025(filename):
    designations = set()
    with gzip.open(filename, "rt") as f:
        for line_num, line in enumerate(f, 1):
            parts = line.strip().split()
            if not parts:
                continue
            packed = parts[0]
            unpacked = unpack_designation(packed)
            if unpacked and unpacked.startswith("2025"):
                designations.add(unpacked)
            if line_num % 100000 == 0:
                print(f"Procesirano {line_num} redova...")
    return sorted(designations)

if __name__ == "__main__":
    filename = "UnnObs.txt.gz"
    print(f"Parsiram fajl {filename} i izdvajam oznake koje počinju sa '2025'...")
    designations = extract_designations_starting_with_2025(filename)
    print(f"Nađeno {len(designations)} oznaka koje počinju sa '2025'.")

    out_file = "designations_2025.txt"
    with open(out_file, "w") as f_out:
        for d in designations:
            f_out.write(d + "\n")

    print(f"Spisak oznaka sačuvan u fajl '{out_file}'.")


# =============================================================================
# import requests
# 
# def download_tmp2_observations(designation):
#     # Pretvori razmake u _
#     filename_part = designation.replace(" ", "_")
#     url = f"https://minorplanetcenter.net/tmp2/{filename_part}.txt"
# 
#     print(f"Skidam: {url}")
#     response = requests.get(url)
# 
#     if response.status_code == 200 and response.text.strip():
#         filename = filename_part + "_obs.txt"
#         with open(filename, "w") as f:
#             f.write(response.text)
#         print(f"Uspešno sačuvano: {filename}")
#     else:
#         print(f"Fajl nije pronađen za: {designation} (možda još nije generisan?)")
# 
# # === Primer ===
# download_tmp2_observations("2025 MJ71")
# 
# =============================================================================

import requests
import time

def generate_and_download(designation):
    base = designation.replace(" ", "%20")
    tmp_filename = designation.replace(" ", "_")
    
    # 1. Otvori show_object da generiše tmp fajl
    trigger_url = f"https://minorplanetcenter.net/db_search/show_object?object_id={base}&commit=Show"
    print(f"Generišem fajl otvaranjem: {trigger_url}")
    r_trigger = requests.get(trigger_url)
    if r_trigger.status_code != 200:
        print(f"Greška prilikom otvaranja stranice za {designation}")
        return

    # 2. Sačekaj da se fajl generiše
    time.sleep(2)  # možeš povećati ako treba

    # 3. Skini tmp fajl
    download_url = f"https://minorplanetcenter.net/tmp2/{tmp_filename}.txt"
    print(f"Pokušavam da skinem: {download_url}")
    r = requests.get(download_url)
    if r.status_code == 200 and r.text.strip():
        with open(f"{tmp_filename}_obs.txt", "w") as f:
            f.write(r.text)
        print(f"Uspešno sačuvano kao {tmp_filename}_obs.txt")
    else:
        print(f"Fajl nije pronađen za: {designation} (možda nije generisan)")

def batch_generate_and_download(filename):
    with open(filename, "r") as f:
        designations = [line.strip() for line in f if line.strip()]

    print(f"Učitano {len(designations)} oznaka.")

    for i, desig in enumerate(designations, 1):
        print(f"[{i}/{len(designations)}] Obrada: {desig}")
        generate_and_download(desig)
        time.sleep(0.5)  # Pauza da ne opteretiš server

if __name__ == "__main__":
    batch_generate_and_download("designations_2025.txt")



    
    
    