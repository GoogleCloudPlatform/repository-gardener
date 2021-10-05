# DPE Bot Webhooks

## Deploy

### Setup runtime config

```
gcloud beta runtime-config configs create --project $PROJECT_ID dpebot

gcloud beta runtime-config configs variables set --project $PROJECT_ID \
  --config-name dpebot --is-text github-user dpebot

# Create a token with the following permissions: admin:repo_hook, delete_repo,
# gist, notifications, repo, user, workflow
gcloud beta runtime-config configs variables set --project $PROJECT_ID \
  --config-name dpebot --is-text github-access-token $GITHUB_ACCESS_TOKEN

export GITHUB_WEBHOOK_SECRET=$(ruby -rsecurerandom -e 'puts SecureRandom.hex(20)')

gcloud beta runtime-config configs variables set --project $PROJECT_ID \
  --config-name dpebot --is-text github-webhook-secret \
  $GITHUB_WEBHOOK_SECRET

gcloud beta runtime-config configs variables set --project $PROJECT_ID \
    --config-name dpebot --is-text github-webhook-url \
    https://$PROJECT_ID.uc.r.appspot.com/webhook
```

### Deploy to App Engine

```
gcloud app deploy --project=$PROJECT_ID
```
