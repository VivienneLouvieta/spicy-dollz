# Spicy Dollz — backend

Your original prototype, connected to a real server. The design is unchanged. Everything that used to live only in the browser now goes through the API.

## What the server handles

| Area | What it does |
| --- | --- |
| Accounts | Sign up and sign in with email or name. Passwords are hashed with scrypt. Sessions use bearer tokens. Each account keeps its colour card, and sign-in attempts are rate-limited. Rename, change password, delete account, and password reset by email (needs SMTP). |
| Wallet | The server tracks balances and transaction history. Every purchase, tip, subscription, conversion and withdrawal runs in a locked database transaction, so balances can't race or go negative. |
| Payments | Spicy Dollz top-up packs and Spicy Premium plans go through Stripe Checkout. The checkout opens in a new tab, the server checks the payment with Stripe, and coins are credited exactly once. A signed Stripe webhook is also supported. Without a Stripe key, the server runs in test mode and payments are free. |
| Creator economy | Fans tip creators and subscribe for 900 coins a month. The money lands in the creator's Tips or Subscriptions balance. Only earned money can be withdrawn; topped-up coins stay in the app. Withdrawals are saved as `pending` requests for you to pay out. |
| Uploads | Profile photos, Premium banners and videos. The server checks the real file type, and if `ffprobe` is installed it also checks the real duration (Premium videos need at least 2:00) and builds the thumbnail. |
| Locked videos | Subscribers-only and Premium videos play only for the owner or an active subscriber. They're served through signed links that expire after 6 hours. |
| Profiles | Open `#@handle` to see another creator's profile, with their bio, links, photo, banner, featured photos and posts. Follow, subscribe and tip there. Views, followers and likes are real counts. |
| Posts | Videos and photos. Captions turn `#hashtags` into tags. Thumbnails of locked posts are blurred on the server, so subscriber content can't leak through the preview image. |
| Reels and Home | Reels is a feed of every creator's posts, ranked by likes, comments, views and age, with a boost for people you follow and your Tag Preferences. Home shows popular posts, top and newest creators, popular tags and per-tag rows. Search finds creators and tags. |
| Social | Likes, comments (delete your own or comments on your posts), follows, follower lists, a Liked tab, and view counting (one view per person per 30 minutes). |
| Inbox | Direct messages between users, refreshed every few seconds while a chat is open. Messages from people you don't follow and haven't replied to land in Requests. General shows notifications for follows, likes, comments, tips and new subscribers. |
| Stats | Daily views, likes, followers and subscribers for 7 or 30 days. |
| Safety | Block users (they can't message, comment or follow, and their posts are hidden). Report posts, comments and accounts. The first account, or any email in `ADMIN_EMAILS`, is an admin and gets a Moderation page in Settings to review reports, remove posts and suspend accounts. |

## Run it yourself

```bash
pip install -r requirements.txt
python3 build.py            # rebuilds public/index.html from original/ + client/
python3 server.py           # http://localhost:8000
```

## Settings (environment variables)

| Variable | Purpose |
| --- | --- |
| `STRIPE_SECRET_KEY` | `sk_test_...` or `sk_live_...`. Turns on real card payments. |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...`. Optional. Point a Stripe webhook at `/api/stripe/webhook` (event `checkout.session.completed`). |
| `PAYMENTS_TEST_MODE` | `1` = free payments for testing. On by default when no Stripe key is set. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` | Password reset emails. |
| `PLATFORM_FEE_PCT` | Share of tips and subscriptions the platform keeps (default 0). |
| `MAX_VIDEO_MB` | Upload limit for videos (default 500). |
| `TRUST_VISITOR_HEADER` | `1` keeps people signed in through the preview proxy's visitor header. Set it to `0` if the server is exposed directly to the internet. |
| `DATA_DIR` | Where the database and media files are stored (default `./data`). |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather. Turns on Sign in with Telegram. |
| `TELEGRAM_BOT_NAME` | The bot's username (without @). |
| `ADMIN_EMAILS` | Comma-separated emails that become admins. If empty, the first account to sign up is the admin. |

## Files

- `server.py`: the whole API (FastAPI + SQLite)
- `client/boot.js`: session restore, API helper, storage that saves to the server
- `client/app-server.js`: wallet sync, real post tiles, creator profiles
- `client/social.js`: reels, home, post viewer, comments, follows, inbox and chat, notifications, stats, blocking, reports and moderation
- `build.py`: applies the integration edits to the original HTML and fails loudly if any edit doesn't match
- `public/index.html`: the built app

## Not connected yet

- Telegram sign-in: create a bot with @BotFather, send `/setdomain` and enter the domain the app runs on (for example `yourname.pplx.app`), then set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_BOT_NAME`. Telegram only works on that exact domain.
- X and Instagram sign-in need OAuth app keys from each provider.
- Withdrawals are recorded, but crypto payouts aren't sent automatically.
- Messages refresh by polling (every 4 s in an open chat, 15 s otherwise), not WebSockets.
- Playlists and the guestbook from the prototype are hidden; they aren't backed by the server.

## Hosting for many users

The database (SQLite) and uploaded files live in `DATA_DIR` on one machine. For a public platform, run the server on a host with a persistent disk (a VPS, or Render/Railway/Fly with a volume), back up `DATA_DIR` regularly, and put it behind HTTPS. With heavy video traffic, move media to object storage (S3, Cloudflare R2) with a CDN, and move the database to Postgres.

An adult-content platform also needs age verification for creators, consent records for everyone who appears in uploads, a takedown process, and terms of service that follow the law where you and your users are.

## Self-hosting with Docker

See `DEPLOY.md`. `docker compose up -d --build` runs the app behind Caddy (automatic HTTPS). All data lives in `./data` (SQLite + media). `deploy/backup.sh` makes a consistent daily backup; admins can also download a full backup from Settings > Backup.
