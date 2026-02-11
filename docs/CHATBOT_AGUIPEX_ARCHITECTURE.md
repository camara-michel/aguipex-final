# Architecture du Chatbot AGUIPEX

## 1. Objectif

Assistant conversationnel **fluide, pédagogique, professionnel** pour le site AGUIPEX, qui :
- Explique AGUIPEX et guide les visiteurs
- S’appuie sur le **contenu du site** (Statistiques, Cartographie, Manifestations, Entreprises, Foires, Produits, Projets, Actualités, Données stratégiques, etc.)
- Utilise une **intelligence hybride** : recherche sémantique + NLP léger + cache
- **Ne invente jamais** de services ; priorité aux données réelles

Ton : clair, humain, rassurant, expert sans jargon.

---

## 2. Architecture technique

### 2.1 Stack

- **Backend** : Django (core)
- **NLP** : extraction de mots-clés (stopwords FR, normalisation), détection d’intention par règles
- **Recherche** : `Q()` sur champs texte (titre, description, detail, etc.) des modèles concernés
- **Cache** : `django.core.cache` pour réponses fréquentes (évite de rejouer recherche + réponse)

### 2.2 Modèles de données

| Modèle           | Rôle |
|------------------|------|
| `ChatSession`    | Session de conversation (session_id unique) |
| `ChatMessage`    | Message utilisateur ou bot (role, content, understood_as) |
| `ExtractedKeyword` | Mots-clés extraits par question (word, weight, session, message) → alimente le **Word Cloud** |

### 2.3 Flux de traitement

1. **Réception** : POST `/api/chatbot/` avec `{ "session_id", "message" }`
2. **NLP** : `extract_keywords(question)` → liste (mot, poids) ; `detect_intent(question, keywords)` → intention (greeting, statistiques, entreprises, etc.)
3. **Cache** : si question normalisée déjà en cache → retourne la réponse mise en cache
4. **Recherche** : `search_site_content(keywords, intent)` sur les modèles : Statistique, Projet, Entreprise, ManifestationCommerciale, Foires, Produit, Actualite, DonneeStrategique, Interprofession
5. **Réponse** : `build_response(question, intent, search_results, keywords)` → (reply, understood_as)
6. **Persistance** : enregistrement du message utilisateur, de la réponse bot, et des mots-clés (pour Word Cloud)
7. **Réponse API** : `{ "reply", "understood_as", "keywords", "session_id" }`

### 2.4 APIs

| Endpoint | Méthode | Rôle |
|----------|--------|------|
| `/api/chatbot/` | POST | Envoyer un message, recevoir la réponse + mots-clés |
| `/api/chatbot/word-cloud/` | GET | Données du Word Cloud (mots agrégés avec poids) ; option `?session_id=` pour une session |
| `/word-cloud/` | GET | **Page** Word Cloud (accès depuis la **navbar**, pas dans le chatbot) |

---

## 3. NLP

- **Mots-clés** : normalisation (minuscules, accents → ASCII), suppression ponctuation, split, suppression stopwords FR et mots &lt; 2 caractères, comptage → tri par fréquence.
- **Intention** : règles basées sur des termes (ex. « statistique », « entreprise », « manifestation », « contact », « aguipex ») pour orienter la recherche et le texte de réponse (salutation, remerciement, thèmes métier).

---

## 4. Word Cloud

- **Source** : table `ExtractedKeyword` (poids = fréquence dans les questions).
- **Agrégation** : par `word`, `Sum(weight)`, ordre `-total_weight`, limite 80–200.
- **Page** : `/word-cloud/` ; affichage en tailles de police proportionnelles au poids, palette AGUIPEX (vert), responsive.
- **Accès** : lien **« Nuage de mots-clés »** dans le menu **Ressources** de la navbar (pas dans l’interface du chatbot).

---

## 5. UI/UX

- **Chatbot** : bouton flottant (icône discussion) ; au clic, panneau avec en-tête « Assistant AGUIPEX », zone messages (user à droite, bot à gauche), ligne « Voici ce que j’ai compris » (sous les messages), champ de saisie + bouton Envoyer. Réponses avec mise en forme **gras** via `**texte**`.
- **Word Cloud** : page dédiée, titre « Nuage de mots-clés », sous-titre explicatif, chargement des données via `/api/chatbot/word-cloud/`, affichage en temps réel.

---

## 6. Bonnes pratiques

- **Sécurité** : utilisation du token CSRF pour POST chatbot.
- **Performance** : cache des réponses, requêtes limitées par modèle (ex. 3 résultats par type).
- **Cohérence** : pas d’invention de contenu ; si rien trouvé, message d’orientation vers les sections du site et la page Contact.
- **Traçabilité** : chaque question/réponse et mots-clés sont en base pour analyse et Word Cloud.

---

## 7. Fichiers principaux

- `core/models.py` : `ChatSession`, `ChatMessage`, `ExtractedKeyword`
- `core/chatbot_services.py` : NLP, recherche, cache, construction de réponse
- `core/views.py` : `chatbot_api`, `word_cloud_data`, `word_cloud_page`
- `core/urls.py` : routes API et page Word Cloud
- `templates/partials/base.html` : widget chatbot (bouton + panneau + JS)
- `templates/aguipex/word_cloud.html` : page Word Cloud
- `core/admin.py` : enregistrement des modèles chatbot
