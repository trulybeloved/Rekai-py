# RE:KAI

## Acknowledgements:

> "If I have seen further, it is by standing on the shoulders of giants." - Sir Issac Newton

This is a side project that I took up on my journey learning to code. And it wouldn't have been possible without the vast number of beautifully written dependances that it's built upon. The open source community is awesome and I'm tremendously grateful to all those who have contibuted to those dependencies. 

I'm also indebted to [Bikatr7](https://github.com/Bikatr7), the author of [Kudasai](https://github.com/Bikatr7/Kudasai) - A Japanese-English preprocessor with automated translation capabilities, for it's "Kairyou" preprocessing module which has been refactored and adapted into Rekai, and their contributions to this project. 

I'm also tremendously greatful to [JanSnoh](https://github.com/JanSnoh) for reviewing the codebase and all the great advice and contributions along the way. 


# Setting up Rekai

## Setting up API access:

This project uses the following APIs:

- **DeepL:**
  - [DeepL API Documentation](https://www.deepl.com/docs-api/)

- **Google Cloud Text-to-Speech:**
  - [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)

- **Google Cloud Translation:**
  - [Google Cloud Translation API Documentation](https://cloud.google.com/translate/docs)

## IMPORTANT: API Costs

**As you are required to use your own API Keys/Authentication, please be aware of the potential risks of generating unintended requests due to programming errors. Kindly take appropriate measures to set up quotas/limitations in the respective API provider consoles/settings.**

The APIs implemented offer generous free quotas per month and should suffice for personal use. 


| Service          | Monthly Free Quota               |                              
|------------------|-----------------------------|
| [Deepl FREE](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-Free) | 500,000 characters/mo       |                                         
| [GCloud TL](https://cloud.google.com/translate/pricing) | 500,000 characters/mo       |                                         
| [GCloud TTS](https://cloud.google.com/text-to-speech/pricing) | WaveNet voices - 4,000,000 characters/mo |                                         
|                  | Neural2 voices - up to 1,000,000 **bytes/mo**  |        

(These values are subject to change. Kindly confirm from official documentation)

## Obtaining DeepL API:

Subscribe to DeepL [here](https://www.deepl.com/pro#developer). The free API does need a valid credit card. Deepl should also be providing it's API sevice in your region. 

The authentication is using an API key and will need to be provided while using Rekai. You can generate/find this in your [account page](https://www.deepl.com/your-account/summary) at Deepl.com

## Setting up Google Cloud APIs:

This project leverages Google Cloud services and requires authentication using the Google Cloud CLI. Follow the steps below to set up authentication and configure your Google Cloud project. Google's Translation API library **for python** does not support API keys. Hence installation of the SDK is necessary for providing Google Translate functionality. 

### Prerequisites


Before you begin, make sure you have the following:

- Google Cloud Account (requires a valid credit card/payment method)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed.
- A Google Cloud project created.
    - This project should have the relevant APIs enabled in the Google Cloud Dashboard. 

### Setup Instructions

#### 1. Install and Initialize Google Cloud SDK

If you haven't installed the Google Cloud SDK, follow the instructions [here](https://cloud.google.com/sdk/docs/install).

Initialize Gooogle Cloud SDK by following the instructions [here](https://cloud.google.com/sdk/docs/initializing)

#### 2. Authenticate with Google Cloud

Run the following command in a terminal application to authenticate with Google Cloud:

```bash
gcloud auth login
```

This will open a browser window prompting you to log in with your Google Cloud credentials.

#### 3. Set Default Project

After successful authentication, set your default project using the following command:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with the actual ID of your Google Cloud project.

#### 4. Verify Configuration

To verify that your configuration is set up correctly, run:

```bash
gcloud config list
```

Make sure that the `project` property is set to your project ID.


#### 5. Set up Application Default Credentials

This is applicatble if you are running Rekai in a local environment, like your own personal computer.

Read more about it [here](https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to)

Create the credential file by running:

```bash 
gcloud auth application-default login
```
This may once again open a browser window prompting you to log in with your Google Cloud credentials.

#### 6. Done. 

You should now be able to use Google Cloud APIs within Rekai.

### Troubleshooting

If you encounter any issues during the setup process, refer to the [Google Cloud SDK documentation](https://cloud.google.com/sdk/docs/troubleshooting) for troubleshooting tips.

