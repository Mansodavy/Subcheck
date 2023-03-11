import requests
import re
import concurrent.futures

# Inviter l'utilisateur à saisir le domaine qu'il souhaite rechercher pour les sous-domaines
domain = input("Entre le domain que tu souhaite pour récupérer les sous domaine en ligne : ")

# Faire une demande au site crt.sh pour obtenir une liste de sous-domaines pour le domaine
url = f"https://crt.sh/?q=%25.{domain}&output=json"
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print(f"HTTP error: {errh}")
    quit()
except requests.exceptions.ConnectionError as errc:
    print(f"Connection error: {errc}")
    quit()
except requests.exceptions.Timeout as errt:
    print(f"Timeout error: {errt}")
    quit()
except requests.exceptions.RequestException as err:
    print(f"Request error: {err}")
    quit()

# Analyser la réponse JSON pour extraire les sous-domaines
try:
    subdomains = set()
    for result in response.json():
        name_value = result["name_value"].replace("\\n", "\n")
        subdomain = re.search(r"\w.*\." + domain, name_value)
        if subdomain:
            subdomains.add(subdomain.group())
except ValueError as e:
    print(f"JSON parsing error: {e}")
    quit()

# Vérifier si chaque sous-domaine est en ligne et enregistrer les URL des sous-domaines en ligne dans un fichier text
filename = "online_subdomains.txt"
with open(filename, "w") as f:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(requests.get, f"https://{subdomain}"): subdomain for subdomain in subdomains}
        for future in concurrent.futures.as_completed(future_to_url):
            subdomain = future_to_url[future]
            try:
                response = future.result()
                if response.status_code == 200:
                    f.write(f"https://{subdomain}\n")
                    print(f"https://{subdomain} est en ligne et a été ajouté au fichier {filename}!")
            except requests.ConnectionError:
                pass
