# Chat + members setup (free Firebase)
1. console.firebase.google.com > Add project (no Analytics needed).
2. Build > Authentication > Get started > enable **Anonymous** and **Email/Password**. Users tab > Add user: your email + your owner password (this password is your owner code).
3. Authentication > Settings > Authorized domains > add `YOURNAME.github.io`.
4. Build > Firestore Database > Create (production mode). Rules tab: paste firestore.rules (change the email inside to yours) > Publish.
5. Project settings > Your apps > Web (</>) > copy the config into config.js. Set OWNER_EMAIL there too.
6. Upload config.js, community.js, alerts.js, index.html to your repo.
Join code: 092962 (change JOIN_CODE in config.js). Owner: click "Owner login" on the join screen.
