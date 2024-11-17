# Door Access System

This project allows you to control a door access system using Google Cloud Run and Twilio.

## Setup Instructions

1. **Copy Configuration File**
   - Copy `config.yaml.example` to `config.yaml`.
   - Replace the whitelist numbers and door codes in `config.yaml`.

2. **Google Cloud Run Account**
   - Get a Google Cloud Run account if you don't have one.

3. **Deploy to Google Cloud Run**
   - Deploy the function to Google Cloud Run using the supplied script:
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
   - The script will print out the URL at which the function is being served.

4. **Twilio Account**
   - Get a Twilio account.
   - Ensure it is using the latest Google Voice transcription API.
   - Add your Twilio phone number to the whitelist in the [config.yaml](http://_vscodecontentref_/1) file.

5. **Configure Buzzbox**
   - Make sure your buzzbox is configured to point to your Twilio phone number.
   - If your buzzbox is already configured to go to your Google Fi number, forward it to the Twilio number.

6. **Point Twilio Voice Webhook**
   - Point the Twilio voice webhook to the Google Cloud Run URL.

## Usage

- Call the buzzbox.
- It will prompt you for the secret code.
- If you provide one of the secret codes, it will dial the digit configured in the [config.yaml](http://_vscodecontentref_/2) file, opening the door.