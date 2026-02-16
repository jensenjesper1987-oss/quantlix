# Quantlix Customer Portal

Next.js app for the Quantlix customer portal at [app.quantlix.ai](https://app.quantlix.ai).

## Features

- **Sign in** — Email + password (uses API login)
- **Dashboard** — Account info, plan, usage
- **Upgrade to Pro** — Redirects to Stripe Checkout
- **Manage billing** — Redirects to Stripe Customer Portal

## Setup

1. Copy env example and configure:

   ```bash
   cp .env.local.example .env.local
   ```

   Set `NEXT_PUBLIC_API_URL` to your API (e.g. `http://localhost:8000` for local dev).

2. Install and run:

   ```bash
   npm install
   npm run dev
   ```

   Portal runs at http://localhost:3001 (avoids conflict with Grafana on 3000).

## Production

- Build: `npm run build`
- Start: `npm start`
- Set `NEXT_PUBLIC_API_URL` to your API URL (e.g. `https://api.quantlix.ai`)

## Backend requirements

- API must have CORS enabled for the portal origin
- Stripe must be configured: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID_PRO`, `STRIPE_WEBHOOK_SECRET`
- Webhook URL: `https://api.quantlix.ai/billing/webhook`
