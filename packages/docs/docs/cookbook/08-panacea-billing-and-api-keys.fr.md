# Facturation Panacea, Clés API et Mesure de Crédit

Cette recette explique comment Panacea mesure l'utilisation, authentifie les appelants d'API et transforme les abonnements Stripe en un solde de crédit dépensable.

## Ce que vous apprendrez

- Les trois façons dont une requête peut s'authentifier : JWT, jeton de session ou clé API à long terme
- Comment les crédits sont vérifiés et déduits par requête, et comment l'utilisation est enregistrée
- Comment un processus de paiement d'abonnement Stripe se traduit par un solde de crédit actualisé
- Comment les utilisateurs génèrent, listent et révoquent leurs propres clés API
- Les garde-fous contre les abus qui régulent les abonnements nouveaux/modifiés

## Pourquoi cela importe

Panacea n'est pas seulement une démo RAG — c'est un produit mesuré avec de véritables niveaux d'abonnement. Chaque téléchargement de document, chaque complétion de chat ou appel d'évaluation coûte des crédits, et les crédits sont rechargés par un abonnement Stripe actif. Cette recette décrit le cycle complet : comment un appelant prouve qui il est, comment cette identité est tarifée, et comment l'argent (via Stripe) se transforme à nouveau en crédits utilisables.

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/backend/database/db_auth.py` | `extractUserEmailFromRequest()` essaie JWT → jeton de session → clé API dans cet ordre ; `user_has_credits()`, `api_key_user_has_credits()`, `deduct_credits_from_api_key_user()` ; garde-fous contre les abus dans `verifyAuthForNewSubscriptipns()` |
| `Panacea/backend/database/usage.py` | `log_api_usage()` écrit une ligne par requête dans `api_usage` ; `get_usage_summary()` / `get_usage_rows()` alimentent le reporting d'utilisation |
| `Panacea/backend/api_endpoints/payments/handler.py` | `CreateCheckoutSessionHandler`, `CreatePortalSessionHandler`, `StripeWebhookHandler` |
| `Panacea/backend/api_endpoints/generate_api_key/handler.py`, `get_api_keys/handler.py`, `delete_api_key/handler.py`, `refresh_credits/handler.py` | Créer, lister, révoquer des clés API ; recharger manuellement des crédits |
| `Panacea/backend/stripe_config/portal_config.py` | Configuration du portail de facturation Stripe par niveau |

## Comment cela fonctionne

1. **Authentifier.** Chaque route protégée appelle `extractUserEmailFromRequest(request)`, qui lit l'en-tête `Authorization: Bearer <token>` et essaie, dans cet ordre : décoder comme un JWT, rechercher comme un jeton de session (`user_email_for_session_token`), puis rechercher comme une clé API (`user_email_for_api_key`). Celui qui réussit en premier résout l'email de l'appelant.
2. **Vérifier les crédits.** Avant de servir une requête, le backend appelle `user_has_credits(user_email)` (appelants JWT/session) ou `api_key_user_has_credits(api_key)` (appelants par clé API) pour confirmer que la colonne `credits` de l'utilisateur dans `users` est d'au moins 1.
3. **Déduire et enregistrer.** À l'achèvement, `deduct_credits_from_api_key_user()` décrémente le solde et `log_api_usage()` insère une ligne dans `api_usage` avec l'endpoint, le modèle, les comptes de jetons et les crédits dépensés — c'est ce qui alimente `GET /v1/usage` et `GET /v1/account`.
4. **Mise à niveau via Stripe.** Le frontend appelle `POST /createCheckoutSession`, qui touche `CreateCheckoutSessionHandler` : il résout l'utilisateur, associe le `product_hash` demandé à un ID de prix Stripe, et crée une `stripe.checkout.Session` en mode `subscription` (appliquant éventuellement un code d'essai gratuit de 30 jours).
5. **Webhook complète la boucle.** Stripe rappelle `POST /stripeWebhook` sur `checkout.session.completed` ; `StripeWebhookHandler` enregistre le nouvel abonnement via `add_subscription()` et appelle `refresh_credits(user_email)` pour recharger le solde de l'utilisateur. Les événements `customer.subscription.updated` (annulation) et `.deleted` sont gérés de manière symétrique.
6. **Gérer l'abonnement.** `POST /createPortalSession` (`CreatePortalSessionHandler`) ouvre une session de portail de facturation Stripe limitée au niveau actuel de l'utilisateur via `config_for_payment_tiers()`, de sorte que les mises à niveau/dégradations/annulations se produisent via l'interface hébergée de Stripe.
7. **Clés API.** `POST /generateAPIKey` nécessite au moins 1 crédit et appelle `generate_api_key()` ; `GET /getAPIKeys` et `POST /deleteAPIKey` listent/révoquent les clés, chacune suivie d'un horodatage `last_used` (`touch_api_key_last_used`).

### Garde-fous contre les abus

`verifyAuthForNewSubscriptipns()` dans `db_auth.py` limite les nouveaux abonnements par niveau par jour (par exemple, 25/jour pour Premium, 5/jour pour Enterprise), envoie une alerte interne par e-mail à des seuils définis (5, 10, 50, 100, 200, 500 nouveaux abonnements/jour), et bloque un utilisateur de changer de plan plus d'une fois par mois glissant.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`) :

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Définissez ces valeurs dans `backend/.env` pour exercer le flux de facturation :

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=some-dev-secret
```

Transférez les webhooks Stripe vers votre backend local avec le Stripe CLI :

```bash
stripe listen --forward-to localhost:5000/stripeWebhook
```

### Essayez-le

```bash
# Générer une clé API (nécessite un JWT/session authentifié, et >=1 crédit)
curl -X POST http://localhost:5000/generateAPIKey \
  -H "Authorization: Bearer <jwt_or_session_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "ma première clé"}'

# Vérifier l'utilisation avec la nouvelle clé API
curl http://localhost:5000/v1/usage \
  -H "Authorization: Bearer <api_key>"
```

## Remarques pour le livre de recettes

Associez cela avec la recette 07 (Passerelle API compatible OpenAI) — les mêmes clés API générées ici sont celles qui authentifient les appels `AnoteOpenAI`. Il est utile de signaler la faute de frappe `verifyAuthForNewSubscriptipns` dans le nom de la fonction comme une particularité connue si un lecteur va la chercher dans le code.
