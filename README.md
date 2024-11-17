  ## deploy
  
  ```sh
  gcloud functions deploy opendoor \
    --gen2 \
    --runtime=python312 \
    --region=us-west1 \
    --source=. \
    --entry-point=voice \
    --trigger-http \
    --allow-unauthenticated
  ```