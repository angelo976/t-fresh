import http.server
import socketserver
import os

# --- CREATION DES DOSSIERS DU SITE ---
if not os.path.exists("site"):
    os.makedirs("site")
if not os.path.exists("site/img"):
    os.makedirs("site/img")

 --- CONTENU HTML ---
html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T-FRESH – Le T-shirt rafraîchissant</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
    <div class="logo">T‑FRESH</div>
    <nav>
        <a href="#concept">Concept</a>
        <a href="#collection">Collection</a>
        <a href="#contact">Contact</a>
           T‑FRESH utilise un coton de haute qualité combiné à une technologie innovante 
        qui permet de maintenir votre corps au frais même lors des fortes chaleurs.
    </p>

    <div class="features">
        <div class="feature-card">
            <h3>🌡️ Technologie rafraîchissante</h3>
            <p>Des fibres qui régulent la température et absorbent l'humidité.</p>
        </div>

        <div class="feature-card">
            <h3>🇫🇷 Fabriqué en France</h3>
            <p>Une qualité supérieure et un savoir‑faire local.</p>
        </div>

        <div class="feature-card">
            <h3>🧼 Coton premium</h3>
            <p>Une matière douce, respirante et durable.</p>
        </div>
    </div>
</section>

<section id="collection" class="section">
    <h2>Nos modèles</h2>
    <p>Disponibles pour femmes, hommes et enfants.</p>

    <div class="products">
        <div class="product-card">
            <img src="img/homme.jpg" alt="T-shirt homme">
            <h3>Modèle Homme</h3>
            <p>Blanc – Coupe moderne</p>
            <span class="price">49,90€</span>
        </div>

        <div class="product-card">
            <img src="img/femme.jpg" alt="T-shirt femme">
            <h3>Modèle Femme</h3>
            <p>Blanc – Coupe ajustée</p>
            <span class="price">49,90€</span>
        </div>

        <div class="product-card">
            <img src="img/enfant.jpg" alt="T-shirt enfant">
            <h3>Modèle Enfant</h3>
            <p>Blanc – Ultra léger</p>
            <span class="price">34,90€</span>
        </div>
    </div>
</section>

<footer id="contact">
    <h3>Contact</h3>
    <p>Email : contact@t-fresh.fr</p>
    <p>© 2026 T‑FRESH – Tous droits réservés</p>
</footer>

</body>
</html>
"""

# --- CONTENU CSS ---
css_content = """
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #ffffff;
    color: #1b1b1b;
}
header {
    display: flex;
    justify-content: space-between;
    padding: 20px 10%;
    background: #eaf6ff;
    position: fixed;
    width: 100%;
    top: 0;
}
.logo {
    font-size: 28px;
    font-weight: bold;
    color: #0077cc;
}
nav a {
    margin-left: 20px;
    font-weight: bold;
    text-decoration: none;
    color: #0077cc;
}
.hero {
    padding: 200px 10% 120px;
    text-align: center;
    background: linear-gradient(#ffffff, #cfeaff);
}
.cta {
    background: #0077cc;
    color: white;
    padding: 12px 25px;
    border-radius: 6px;
    text-decoration: none;
}
.section {
    padding: 70px 10%;
    text-align: center;
}
.features, .products {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
}
.feature-card, .product-card {
    background: #f2f8ff;
    padding: 20px;
    border-radius: 10px;
    width: 280px;
}
.product-card img {
    width: 100%;
    border-radius: 8px;
}
.price {
    font-weight: bold;
    color: #0077cc;
}
footer {
    background: #eaf6ff;
    padding: 40px;
    text-align: center;
}
"""

# --- CREATION DES FICHIERS ---
with open("site/index.html", "w", encoding="utf8") as f:
    f.write(html_content)

with open("site/style.css", "w", encoding="utf8") as f:
    f.write(css_content)

print("✔ Fichiers HTML/CSS générés.")

# --- SERVEUR WEB ---
PORT = 8080
os.chdir("site")

handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"🚀 Site T-FRESH lancé sur http://localhost:{PORT}")
    httpd.serve_forever()
