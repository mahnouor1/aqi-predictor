# 🤖 AQI Predictor - True Automation Setup

## 🎯 The Problem
GitHub scheduled runs (cron) are not working for your repository. This is common with free accounts.

## ✅ The Solution
Use external services to trigger your GitHub workflow every hour.

## 🚀 Setup Instructions

### Option 1: GitHub Actions (Try This First)

1. **Enable Scheduled Runs:**
   - Go to your repository settings
   - Click "Actions" → "General"
   - Under "Workflow permissions", enable "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

2. **Test the Schedule:**
   - Go to Actions tab
   - Look for "Real AQI Predictor Deployment"
   - Check if it runs automatically

### Option 2: External Cron Service (Guaranteed to Work)

1. **Sign up for a free cron service:**
   - [cron-job.org](https://cron-job.org) (Free)
   - [EasyCron](https://www.easycron.com) (Free tier)
   - [UptimeRobot](https://uptimerobot.com) (Free)

2. **Create a new cron job:**
   - **URL:** `https://api.github.com/repos/mahnouor1/aqi-predictor/dispatches`
   - **Method:** POST
   - **Headers:** 
     ```
     Authorization: token YOUR_GITHUB_TOKEN
     Accept: application/vnd.github.v3+json
     ```
   - **Body:**
     ```json
     {
       "event_type": "hourly-trigger",
       "client_payload": {
         "timestamp": "{{timestamp}}",
         "trigger": "external-cron"
       }
     }
     ```
   - **Schedule:** Every hour (0 * * * *)

3. **Get GitHub Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate new token with "repo" permissions
   - Use this token in the cron service

### Option 3: Vercel Cron (If You Deploy to Vercel)

Create `vercel.json`:
```json
{
  "crons": [
    {
      "path": "/api/trigger-github",
      "schedule": "0 * * * *"
    }
  ]
}
```

## 🎯 Recommended Solution

**Use cron-job.org (Free & Reliable):**

1. Go to [cron-job.org](https://cron-job.org)
2. Sign up for free account
3. Create new cron job:
   - **Title:** AQI Predictor Hourly
   - **URL:** `https://api.github.com/repos/mahnouor1/aqi-predictor/dispatches`
   - **Method:** POST
   - **Headers:** `Authorization: token YOUR_TOKEN`
   - **Body:** `{"event_type": "hourly-trigger"}`
   - **Schedule:** Every hour
4. Save and activate

## ✅ Verification

After setup, you should see:
- New deployments every hour
- Real-time data fetching
- Model training with new data
- Automatic commits to repository

## 🔧 Troubleshooting

If it still doesn't work:
1. Check GitHub token permissions
2. Verify the repository dispatch URL
3. Test with manual trigger first
4. Check GitHub Actions logs
