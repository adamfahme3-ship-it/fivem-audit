# FiveM Audit Starter

This is a transparent, opt-in anti-cheat/audit starter. It has three parts:

1. `agent/Scan-FiveMClient.ps1` — visible PIN-entry Windows scanner run by the PC owner. It audits only documented FiveM/GTA folders and matching running-process names.
2. `resource/` — install in your FiveM server's `resources` folder. It creates a temporary player link code and displays it to the player.
3. `api/audit_api.py` — a small private API that receives server-created sessions and opt-in agent reports.

The browser, the resource, and the API **cannot silently scan a player's PC**. The user must download/run the agent, see what it checks, and supply their temporary link code. The agent is read-only and never deletes, uploads arbitrary files, or enumerates personal folders.

## Setup

1. Put `resource` in your server's resource folder as `ac_audit`, then add `ensure ac_audit` to `server.cfg`.
2. Copy `resource/config.lua.example` to `resource/config.lua`, set the API URL and long random `serverSecret`.
3. On a private HTTPS host, run `python audit_api.py --secret YOUR_SERVER_SECRET --port 8080`. Put it behind an HTTPS reverse proxy before use on the internet.
4. Tell the player their `/auditcode` code in game. They download the agent and run:

```powershell
powershell -STA -ExecutionPolicy Bypass -File .\Scan-FiveMClient.ps1 -Endpoint "https://audit.example.com/reports"
```

5. Open the API root (`https://audit.example.com/`) on an authorized staff workstation to use the status dashboard. The API stores reports in `data/reports/` for review.

## Standalone mode (no FiveM server resource)

You do not need to install `resource/`. Start the private API and open its dashboard yourself. Enter your staff secret, write the player's name or Discord ID, then select **Create scan PIN**. Send the player the scanner download link plus their PIN. They enter it in the scanner and explicitly approve the audit. Refresh the dashboard to see the submitted status.

## Deploy on Render

1. Create a new empty GitHub repository and upload the **contents** of this folder (including `render.yaml`). Do not upload the parent folder itself.
2. In Render, select **New** → **Blueprint**, connect the GitHub repository, then click **Apply**. Render will generate `AUDIT_SECRET` for you.
3. When deployment completes, open the `onrender.com` URL. This is your staff dashboard. Keep the `AUDIT_SECRET` private; copy it from Render's Environment page and enter it in the dashboard when prompted.
4. Give a player the agent file and tell them to run the command below, replacing `YOUR-APP` with the Render subdomain:

```powershell
powershell -STA -ExecutionPolicy Bypass -File .\Scan-FiveMClient.ps1 -Endpoint "https://YOUR-APP.onrender.com/reports"
```

Render's free web services can sleep when unused and do not provide durable local disk. This starter is suitable for trials; use authenticated durable storage before relying on it for real moderation records.

## Important deployment notes

- This starter is for legitimate server administration with player notice and consent. Publish what the agent checks, retention period, and appeal/review process.
- Treat all reports and game-client events as potentially forged. Use reports as a moderation signal, never as your only automatic ban criterion.
- Set `serverSecret` to a high-entropy secret and never distribute it to players. Require HTTPS; this sample deliberately rejects remote HTTP endpoints in the agent.
- This is a detection/audit baseline, not an Echo AC replacement. Production software needs code signing, server-side account linking, durable storage, rate limiting, reviewed rules, privacy controls, telemetry hardening, and a false-positive workflow.
