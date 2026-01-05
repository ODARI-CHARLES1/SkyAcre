
export const welcomeTemplate=(name)=>{
     const currentYear = new Date().getFullYear();
    const template=`
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Welcome to SkyAcre</title>
      <style>
        body { margin:0; padding:0; background-color:#f4f7f6; font-family:Arial, sans-serif; color:#223; }
        .container { max-width:680px; margin:28px auto; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 8px 30px rgba(25,40,60,0.06); }
        .header { padding:18px 22px; }
        .brand { font-size:24px; font-weight:700; color:#0b2b18; }
        .hero { width:100%; display:block; }
        .content { padding:26px; }
        a{color:white;}
        h1 { margin:0 0 10px 0; font-size:22px; line-height:1.2; color:#0b2b18; }
        p { margin:0 0 16px 0; color:#3b4b42; line-height:1.5; font-size:15px; }
        .cta { display:inline-block; text-decoration:none; background-color:#2e9e49;  padding:12px 20px; border-radius:10px; font-weight:600; box-shadow:0 6px 18px rgba(46,158,73,0.18); }
        .small { font-size:13px; color:#6b7b71; margin-top:18px; }
        .footer { padding:18px 26px; border-top:1px solid #eef3ef; font-size:13px; color:#7b8a81; background:#fbfdfb; }
      </style>
    </head>
    <body>
      <div class="container" role="article" aria-label="Welcome to SkyAcre">
        <div class="header">
          <div class="brand">Sky<span style="color: green;">A</span>cre</div>
          <div style="font-size:12px;color:#6b7b71;margin-top:2px;">Smart tools for modern farming</div>
        </div>

        <img src="https://i.pinimg.com/736x/49/59/0f/49590fb9ccc625f9d30ffe36f57e9235.jpg"
          alt="Farm fields and sunrise — welcome to AgrFly"
          class="hero"
          style="display:block;width:100%;height:auto;max-height:380px;object-fit:cover;"
        />

        <div class="content">
          <h1>Welcome, ${name} 👋</h1>

          <p>
            Your SkyAcre account has been created successfully. We’re excited to have you on board!
            You now have access to farm management tools, crop analytics, marketplace connections, and real-time recommendations to help your operation thrive.
          </p>

          <p style="margin-bottom:20px;">
            Get started now by visiting your dashboard and setting up your farm profile.
          </p>

          <a style="color:white;" href="https://sky-acre.vercel.app/" class="cta">Go to SkyAcre Dashboard</a>

          <p class="small">
            If that button doesn’t work, copy and paste this link into your browser:
            <br/><a href="https://sky-acre.vercel.app/" style="color:#2e9e49;text-decoration:none;">https://sky-acre.vercel.app/</a>
          </p>

          <p class="small" style="margin-top:16px;">
            Need help? Reply to this email or visit our <a href="https://sky-acre.vercel.app/" style="color:#2e9e49;">support page</a>.
          </p>
        </div>

        <div class="footer">
          SkyAcre • Helping farmers grow smarter<br/>
          <span style="display:inline-block;margin-top:6px;">© ${currentYear} SkyAcre. All rights reserved.</span>
        </div>
      </div>
    </body>
    </html>
    `
    return template;
}