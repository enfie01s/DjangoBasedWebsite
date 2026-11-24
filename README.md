# DjangoBasedWebsite

The Django site that serves aristia.net until ari-site replaces it.

## Production (Docker)

It runs on the server in `/srv/aristia/websitedj`, owned by `aristia`, as one container (`websitedj-web-1`)
in `aristia`'s own (rootless) Docker. Host nginx terminates TLS for `aristia.net` and `www.aristia.net` and
proxies to `127.0.0.1:SITE_PORT` (21030). There is no test copy: it deploys straight to the live site.

- gunicorn serves the app on port 8000; WhiteNoise serves `/static/` from the image.
- Uploads live in `media/` in the checkout (not in git), mounted into the container and served at `/media/`.
- The container runs as root inside `aristia`'s Docker, which is `aristia` on the server, so uploads stay
  owned by `aristia`.
- The database is the host's MariaDB, reached as `host.docker.internal`, which `compose.own-docker.yml`
  maps to the server's own address (`HOST_IP`): rootless Docker can't reach the host's loopback.
- Settings come from `.env.production` (`chmod 600`, never in git); see `.env.production.example`.

Deploy a new version from `main`:

```bash
cd /srv/aristia/websitedj
git pull --ff-only
export DOCKER_HOST=unix:///run/user/1010/docker.sock
docker compose -f compose.production.yml -f compose.own-docker.yml --env-file .env.production up -d --build
```

Logs: the same `docker compose … logs -f web`, with `DOCKER_HOST` set.

Without `compose.own-docker.yml` and `DOCKER_HOST`, `compose.production.yml` alone runs it in the server's
Docker behind the shared Traefik proxy (as before), as the `APP_UID`/`APP_GID` user.

### Handing aristia.net to ari-site

ari-site also runs in `aristia`'s Docker, on its own port (21021). Promote it (`bash deploy/prod.sh` in
`/srv/aristia/ari-site`), then point `aristia.net`'s nginx at that port instead of 21030 and stop this one
(`docker compose … down`, with `DOCKER_HOST` set). To go back, point nginx at 21030 again.
