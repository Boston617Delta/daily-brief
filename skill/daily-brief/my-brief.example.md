# My brief

Copy this file to `my-brief.md` in the same folder and make it yours, or ask your agent to "set up my daily brief" and it will ask you a few questions and write it for you. `my-brief.md` is excluded from Git at any depth in this repo. Your assistant reads it when building the brief, so its privacy settings apply. If you save it inside another repository, add an ignore rule there too. The names and clients below are sample placeholders; replace them with your own details.

## About me

- Name: Sam
- Home: Boston, MA
- Time zone: America/New_York
- Units: f (use c for Celsius)
- Work days: Mon to Fri
- Non-work days: keep my configured sections (or name the sections to skip)
- Weather source: web (or open-meteo for personal non-commercial use, or open-meteo-commercial with a subscription and OPEN_METEO_API_KEY set in the environment)

Never put passwords, API keys, tokens, or other credentials in this file.

## Where my stuff lives

Name the tools your agent should look in. Leave a line blank if you don't use it.

- Calendar: Google Calendar, work and personal
- Email: Gmail (work address first, then personal)
- Chat: Slack
- Projects and tasks: Asana tasks assigned to me, plus `~/notes/projects/`
- Clients and deliverables: the "Clients" board in Asana, one project per client (or a spreadsheet, a Notion database, a folder per client)
- Clients on retainer: Acme Dental (SEO, monthly report due the 5th), Northside Bakery (social, 12 posts a month), Harbor Law (ads, weekly report every Friday)
- People who always matter: my manager, any client
- Senders to ignore: newsletters, LinkedIn, receipts

## My sections

This list is the brief. Each line is one section, in the order it appears. The words after the colon tell the agent what to pull and how much to say.

- Delete a line to drop that section.
- Move a line to reorder.
- Reword a line to change what it covers.
- Add a line for anything else, in plain English. Say where to look and what you want back.

Sections:

- Weather: today and tomorrow for my home city, plus anything that changes plans
- Schedule: today's meetings in time order, overlaps flagged, and anything tomorrow I should prepare for today
- Needs you today: emails, messages, and tasks that cost me something if they wait until tomorrow
- Clients: one block per retainer client with each deliverable this month, its status, and what's next, flagging anything overdue or waiting on the client
- Projects: one line per active project on where it stands and what's next
- Markets: ^GSPC, ^IXIC, ^DJI, BTC-USD, AAPL, NVDA (price, daily change, and the headline behind the biggest move)
- Handled: what closed since yesterday's brief

## Section ideas

Copy any of these up into My sections and edit to fit. They're starting points, not a fixed menu.

- Industry news: two headlines from the last day about [your field], with links
- Competitors: anything [competitor names] announced or posted in the last day
- Sales pipeline: deals in [CRM] that moved stages yesterday or have a close date this week
- Sales follow-ups: next actions due or overdue in [CRM], deals with no next action, and proposals or renewals due this month
- Waiting on: approvals and promised replies in [email or tracker] that are overdue or need a follow-up today
- Capacity: meetings and deadlines against available work hours today, plus retainer hours used and remaining in [time tracker]
- Leads: new form fills, calls, or booking requests since yesterday from [source]
- Invoices and bills: anything due or overdue this week in [accounting tool]
- Website: yesterday's visits and top page from [analytics tool], compared to the same day last week
- Social: comments, DMs, and mentions on [accounts] that need a reply
- Reviews: new reviews on [Google, Yelp, Clutch] since yesterday
- Content: what's scheduled to post today and what's due to draft
- Team: who's out today and anything a teammate is blocked on
- Travel: flights, hotels, and confirmations for trips in the next 7 days
- Family: school events, pickups, and appointments on [family calendar]
- Logistics: leave-by times, travel buffers, and who owns each pickup or family obligation in [shared calendar]; flag conflicts, and label unknown travel times or owners
- Health: today's workout from [plan or app]
- Reading: one article from my saved list or [newsletter] worth 10 minutes today
- Quote or word of the day: something short to start on

## Schedule controls

- Enabled: true (false stops brief gathering and delivery)
- Paused until: (blank, indefinite, or an exact date/time in my time zone)
- Schedule reference: (the host's name or ID for this brief's schedule, if one exists)
- Missed runs: skip (or catch-up)
- Catch-up window: 2 hours (used only for catch-up; send at most one current brief)

Ask for "pause until Monday," "stop my brief," "resume it," or "move it to 8 AM." The agent checks the named host job and reports the state and next run. Changing this file alone may not change a cloud job's saved instructions, so verify that the actual schedule was updated. Resuming doesn't send a backlog.

## Delivery

Choose where the brief arrives. Each external channel needs a supported host delivery feature or a connected service. These are delivery preferences, not built-in messaging accounts.

- Delivery: chat (in this assistant; or whatsapp, telegram, sms, email)
- Delivery destination: (your own verified number with country code, email address, or private chat ID; leave blank for chat)
- Delivery connection: (the host's native route or the connected tool/service to use)
- send_brief_to_self: false (true only when you explicitly want delivery to yourself through this channel and destination; false gives an unsent preview or email draft)
- Delivery time: on demand (or 7:00 AM America/New_York on my work days)
- Delivery content: full (or digest; the setup default for SMS is digest)
- External privacy: full (or discreet to omit client/person names, financial amounts, contact details, and sensitive business discussion from all outgoing channels)
- SMS long briefs: shorten (or multipart if you agree to multiple messages and any provider charges)

For example: "Send my brief to me on Telegram at 7 AM on work days, using my connected bot and my private chat." The setup interview records that delivery request and its destination. Changing the channel or destination requires your direct instruction. Setting a time here doesn't create a schedule by itself; ask the assistant to schedule it and check that the host supports it.

Keep bot tokens, API keys, and passwords in your host's connection settings or secret manager, never in this file. The assistant confirms when a connection is missing and returns the brief in its own result rather than silently switching channels.

## Output

- Format: auto (Markdown in chat, simple text in messaging, a readable email body; or markdown, plain-text, html)
- Output folder for html: `~/Briefs`
- Length: short (or detailed)
- Project status max age: 7 days (older client/project status is labeled stale; missing update dates are disclosed)

Existing settings using `Format: email` and `send_email_to_self` still work as email-only preferences. An explicit `send_brief_to_self` value takes precedence.
