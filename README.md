# DjangoBasedWebsite

The Django site that serves aristia.net until ari-site replaces it.

## Production (Docker)

It runs on the server in `/srv/aristia/websitedj`, owned by `aristia`, as one container (`websitedj-web-1`)
behind the shared Traefik proxy. Host nginx terminates TLS for `aristia.net` and passes requests to Traefik,
which routes `aristia.net` and `www.aristia.net` to this container. There is no test copy: it deploys
straight to the live site.

- gunicorn serves the app on port 8000; WhiteNoise serves `/static/` from the image.
- Uploads live in `media/` in the checkout (not in git), mounted into the container and served at `/media/`.
- The container runs as the `aristia` user (`APP_UID`/`APP_GID`), so uploads stay owned by `aristia`.
- The database is the host's MariaDB, reached as `host.docker.internal`.
- Settings come from `.env.production` (`chmod 600`, never in git); see `.env.production.example`.

Deploy a new version from `main`:

```bash
cd /srv/aristia/websitedj
git pull --ff-only
docker compose -f compose.production.yml --env-file .env.production up -d --build
```

Logs: `docker compose -f compose.production.yml --env-file .env.production logs -f web`

### Handing aristia.net to ari-site

Both use the same Traefik host rule, so only one may run at a time:

```bash
cd /srv/aristia/websitedj && docker compose -f compose.production.yml --env-file .env.production down
cd /srv/aristia/ari-site && bash deploy/prod.sh
```

To go back, stop ari-site and run the `up -d` command above again. Nginx doesn't change either way.
