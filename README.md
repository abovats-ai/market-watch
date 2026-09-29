# Setup (free)
1. Get a free API key at finnhub.io.
2. Create a GitHub repo, upload these files (keep the .github folder).
3. Repo Settings > Secrets and variables > Actions > New secret: FINNHUB_KEY.
4. Settings > Pages > Deploy from branch > main / root.
5. Actions tab > "update" > Run workflow. Site: https://YOURNAME.github.io/REPO
Edit watchlist.txt / universe.txt anytime. universe.txt is the pool the 5 price tiers pick from.
Updates: the Action refreshes data every 30 min (edit the cron in .github/workflows/update.yml); the open page re-checks every 60 seconds.
