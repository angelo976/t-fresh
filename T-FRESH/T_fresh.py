#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serveur statique pour le dossier ./site avec :
- Génération sitemap.xml (basé sur BASE_URL)
- Génération robots.txt (pointe vers sitemap)
- Création optionnelle du fichier CNAME (GitHub Pages)
- Diagnostics et affichage clair de l'URL

Exemples :
    python site_runner.py
    python site_runner.py --host 0.0.0.0 --port 8891
    python site_runner.py --base-url https://t-fresh.com --brand-domain t-fresh.com
"""

import http.server
import socketserver
import os
import argparse
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, ElementTree

# =========================
# CLI & Paramètres
# =========================
parser = argparse.ArgumentParser(description="Serveur statique + sitemap/robots + CNAME (optionnel)")
parser.add_argument("--base-dir", default="site", help="Dossier où se trouve ton site statique (défaut: site)")
parser.add_argument("--host", default="127.0.0.1", help="Hôte à écouter (0.0.0.0 pour exposition réseau)")
parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8891")), help="Port d'écoute")
parser.add_argument("--base-url", default=os.getenv("BASE_URL", "").strip(),
                    help="URL publique du site, ex. https://t-fresh.com (utile pour sitemap/robots)")
parser.add_argument("--brand-domain", default=os.getenv("BRAND_DOMAIN", "").strip(),
                    help="Nom de domaine de marque (ex. t-fresh.com). Crée/MAJ un fichier CNAME si défini.")
parser.add_argument("--no-serve", action="store_true", help="Ne pas lancer le serveur (juste générer fichiers)")
args = parser.parse_args()

BASE_DIR = args.base_dir
BASE_URL = args.base_url.rstrip("/")
BRAND_DOMAIN = args.brand_domain

IMG_DIR = os.path.join(BASE_DIR, "img")
os.makedirs(BASE_DIR, exist_ok=True)

# =========================
# Diagnostics utiles
# =========================
print("=== DIAGNOSTIC SERVEUR ===")
print("Racine servie   :", os.path.abspath(BASE_DIR))
print("Existe ?        :", os.path.isdir(BASE_DIR))
print("img/ existe ?   :", os.path.isdir(IMG_DIR))
print("Contenu img/    :", os.listdir(IMG_DIR) if os.path.isdir(IMG_DIR) else "(absent)")
print("BASE_URL        :", BASE_URL if BASE_URL else "(non défini)")
print("BRAND_DOMAIN    :", BRAND_DOMAIN if BRAND_DOMAIN else "(non défini)")
print("===========================")

# =========================
# Fichier CNAME (pour GitHub Pages)
# =========================
def ensure_cname(base_dir: str, domain: str):
    if not domain:
        return None
    cname_path = os.path.join(base_dir, "CNAME")
    current = None
    if os.path.exists(cname_path):
        with open(cname_path, "r", encoding="utf-8") as f:
            current = f.read().strip()
    if current != domain:
        with open(cname_path, "w", encoding="utf-8") as f:
            f.write(domain + "\n")
        print(f"[OK] Fichier CNAME créé/mis à jour → {domain}")
    else:
        print(f"[OK] CNAME déjà correct → {domain}")
    return cname_path

ensure_cname(BASE_DIR, BRAND_DOMAIN)

# =========================
# Sitemap.xml
# =========================
def collect_html_files(base_dir: str):
    items = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".html"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir).replace(os.sep, "/")
                # index.html à la racine -> URL / (chemin vide)
                if rel_path == "index.html":
                    url_path = ""
                # sous-dossiers: /section/index.html -> /section/
                elif rel_path.endswith("/index.html"):
                    url_path = rel_path[:-len("index.html")]
                else:
                    url_path = rel_path
                mtime = os.path.getmtime(full_path)
                items.append((url_path, mtime))
    return items

def to_iso_date(ts):
    # YYYY-MM-DD (suffisant pour sitemap)
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()

def write_sitemap(base_dir: str, base_url: str):
    if not base_url:
        print("[AVERTISSEMENT] BASE_URL n'est pas défini. sitemap.xml aura des URL relatives/non publiques.")
    html_files = collect_html_files(base_dir)
    urlset = Element("urlset", {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xmlns:xhtml": "http://www.w3.org/1999/xhtml"
    })

    for path, mtime in sorted(html_files, key=lambda x: (x[0] != "", x[0])):
        # loc : URL absolue si BASE_URL fourni, sinon chemin relatif
        loc = base_url if (path == "" and base_url) else (
            f"{base_url}/{path.strip('/')}" if base_url else path.strip("/")
        )
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = loc
        SubElement(url, "lastmod").text = to_iso_date(mtime)
        if path == "":
            SubElement(url, "changefreq").text = "daily"
            SubElement(url, "priority").text = "1.0"
        else:
            SubElement(url, "changefreq").text = "weekly"
            SubElement(url, "priority").text = "0.6"

    outfile = os.path.join(base_dir, "sitemap.xml")
    ElementTree(urlset).write(outfile, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Sitemap écrit → {outfile}")

write_sitemap(BASE_DIR, BASE_URL)

# =========================
# robots.txt
# =========================
def write_robots(base_dir: str, base_url: str):
    robots_path = os.path.join(base_dir, "robots.txt")
    lines = [
        "User-agent: *",
        "Allow: /",
    ]
    if base_url:
        lines.append(f"Sitemap: {base_url}/sitemap.xml")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] robots.txt écrit → {robots_path}")

write_robots(BASE_DIR, BASE_URL)

# =========================
# Serveur HTTP statique
# =========================
if not args.no_serve:  # <-- ✅ correct ici
    # On sert depuis BASE_DIR
    os.chdir(BASE_DIR)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    handler = http.server.SimpleHTTPRequestHandler

    with ReusableTCPServer((args.host, args.port), handler) as httpd:
        # Infos d'accès
        local_url = f"http://{args.host}:{args.port}"
        print("\n=== ACCÈS AU SITE ===")
        if BASE_URL:
            print(f"🌍 URL publique (BASE_URL) : {BASE_URL}")
            print("   -> Assure les DNS vers ton hébergeur + HTTPS activé.")
        if BRAND_DOMAIN:
            print(f"🏷️ Domaine de marque : {BRAND_DOMAIN} (CNAME généré si GitHub Pages)")
        print(f"🚀 Site T‑FRESH lancé → {local_url}")
        print("Astuce : --host 0.0.0.0 pour le rendre visible sur ton réseau local.")
        print("======================\n")
        httpd.serve_forever()
else:
    print("[INFO] Mode --no-serve : serveur non lancé (génération uniquement).")
