// GitHub Workflow Trigger API
// This can be deployed to Vercel, Netlify, or any serverless platform

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const githubToken = process.env.GITHUB_TOKEN;
  const repoOwner = 'mahnouor1';
  const repoName = 'aqi-predictor';

  if (!githubToken) {
    return res.status(500).json({ error: 'GITHUB_TOKEN not configured' });
  }

  try {
    const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        event_type: 'hourly-trigger',
        client_payload: {
          timestamp: new Date().toISOString(),
          trigger: 'api-endpoint',
          source: 'external-cron'
        }
      })
    });

    if (response.ok) {
      console.log('✅ GitHub workflow triggered successfully');
      return res.status(200).json({ 
        success: true, 
        message: 'GitHub workflow triggered successfully',
        timestamp: new Date().toISOString()
      });
    } else {
      console.error('❌ Failed to trigger GitHub workflow:', response.status);
      return res.status(response.status).json({ 
        error: 'Failed to trigger GitHub workflow',
        status: response.status
      });
    }
  } catch (error) {
    console.error('❌ Error triggering GitHub workflow:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message
    });
  }
}
