# Everbright Cards — Website

A full static website for a greeting card company. No build step, no dependencies — just HTML, CSS, and vanilla JavaScript.

## Pages

| Page | Description |
| --- | --- |
| `index.html` | Home — hero, occasion categories, featured bestsellers, how it works, testimonials, newsletter signup |
| `shop.html` | Shop — full catalog of 20 cards with category filters, live search, and add-to-cart |
| `about.html` | Our Story — company history, values, and team |
| `contact.html` | Contact — info cards, contact form, and FAQ accordion |

## Features

- **Shopping cart** — slide-out drawer with quantity controls and totals, persisted in `localStorage` across pages
- **Category filtering & search** on the shop page, with deep links (e.g. `shop.html?category=birthday`)
- **Responsive layout** — works on desktop, tablet, and mobile with a collapsible nav
- **Zero dependencies** — no frameworks, fonts, or external assets; works fully offline

## Running locally

Open `index.html` directly in a browser, or serve the folder:

```bash
cd website
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Notes

- The contact and newsletter forms are front-end only; wire them to your backend or email service.
- Checkout is a demo flow — integrate a payment provider (Stripe, Shopify Buy Button, etc.) to take real orders.
- Product data lives in `js/main.js` (`PRODUCTS` array) — edit it to add or change cards.
