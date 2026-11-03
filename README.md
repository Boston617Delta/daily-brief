# daily-brief

A morning brief that brings your weather, market watchlist, calendar, email, and projects into a short report you can read in about a minute. It ships as a skill for Claude Code and Codex, plus a copy-paste prompt for Claude Cowork, ChatGPT and Dots, Meta's Muse, Grok, or any assistant that can reach your calendar and inbox. Choose to receive it in the assistant, WhatsApp, Telegram, SMS, or email through a supported host feature or connected delivery service.

It comes with a base set of sections (weather, schedule, what needs you today, retainer clients and where each deliverable stands, projects, markets, and what got handled), and every one of them is yours to cut, reword, or reorder. Add anything your business runs on in plain English: new leads, unpaid invoices, reviews, competitor news, a family calendar. The agent works out where to look and how to report it.

## Make it yours

Your brief is a list in `my-brief.md`. Each line is one section, and the words after the colon say what you want:

```
Sections:

- Schedule: today's meetings, overlaps flagged, and prep for tomorrow
- Needs you today: replies, tasks, and deadlines that can't wait
- Leads: new form fills and calls since yesterday from the website
- Invoices: anything overdue in QuickBooks
- Weather: just the high and whether I need an umbrella
```

That list is this person's entire brief. They deleted the markets, projects, and handled lines, added two lines for the numbers their business lives on, and cut the weather down to the one thing they check.

You don't have to edit the file by hand. Ask your agent to "set up my daily brief" and it asks five short questions, including where and when it should arrive, then writes the settings. Later, "add my Shopify orders to my brief," "drop markets," or "send it to me on Telegram instead" updates the relevant settings. The example file has a list of section ideas to borrow from.

## What it looks like

An illustrative brief with sample names, dates, and prices. Your sections and length can differ.

```
Tuesday, November 3

Nothing on the calendar until 2, then three calls back to back.

Weather: 48° now, high of 61, overcast. Rain is most likely around 6 PM (60%). Sunset 4:35.
Tomorrow: 55 and clear.

Schedule
- 2:00 PM  Weekly sync with the design team
- 3:00 PM  Client check-in, Acme Dental
- 4:00 PM  Vendor demo (runs into the 4:30 hold you set for writing)

Needs you today
1. Maria asked for the signed SOW by end of day so she can open the PO (email, Mon 4:12 PM).
2. The Q4 content calendar is due Wednesday and the draft in Projects has two empty weeks.
3. Tomorrow's 10 AM budget review: the deck Priya shared Friday is still unread.

Clients
- Northside Bakery (social, 12 posts/month): two scheduled posts overdue, 5 of 12 posted so far. Holiday post photos waiting on the client since Thursday.
- Acme Dental (SEO): October report due Thursday, in progress. Two blog posts delivered, one in client review.
- Harbor Law (ads): on track, Friday report due in 3 days.

Projects
- Website rebuild: homepage copy approved, waiting on photos.
- Newsletter: issue 14 drafted, scheduled for Thursday.

Markets
US indices at Monday's close: S&P 500 7,541 (-0.5%) · Nasdaq 25,164 (-1.1%) · Dow 51,984 (-0.7%)
BTC at 7 AM Eastern Tuesday: 77,005 (-0.3% versus the previous UTC daily close)
Chip stocks led the drop after a weak sales forecast from a major supplier.

Handled
- Jordan answered the hosting question in the #website thread, so that's off your list.
- The Thursday 9 AM standup was cancelled by the organizer.

Could not check: Slack
```

## What's in the repo

| Path | What it is |
|---|---|
| `skill/daily-brief/SKILL.md` | The skill. Tells the agent what to gather, how to sort it, and how to write it. |
| `skill/daily-brief/my-brief.example.md` | Your settings: name, home city, where your tools live, your list of sections, a bank of section ideas, and output format. |
| `skill/daily-brief/scripts/brief_data.py` | Weather (Open-Meteo) and market quotes (Yahoo Finance) as JSON. Python 3.9+ standard library. Free endpoints need no API keys; commercial weather uses your subscription key. |
| `prompts/any-assistant.md` | The whole brief as one prompt, for assistants that can't load a skill folder. |

## Install

For the skill version, install [Git](https://git-scm.com/downloads), [Python 3.9 or newer](https://www.python.org/downloads/), and either [Claude Code](https://code.claude.com/docs/en/overview) or [Codex](https://developers.openai.com/codex/cli/). Open that assistant once and sign in before using it on a schedule. The commands below run in Terminal on macOS or Linux. Choose the block for your assistant; if you've already cloned this repo, skip its `git clone` line and run the remaining commands from the folder containing `daily-brief`.

For an assistant without terminal access, skip to the copy-paste version below.

### Claude Code

```bash
git clone https://github.com/Boston617Delta/daily-brief.git
mkdir -p ~/.claude/skills
cp -R daily-brief/skill/daily-brief ~/.claude/skills/
```

Open Claude Code and ask it to "set up my daily brief," or use `/daily-brief` and ask for setup. It saves `my-brief.md` inside `~/.claude/skills/daily-brief/`. You can also copy `my-brief.example.md` there as `my-brief.md` and edit it yourself. Then ask for "my daily brief."

Connect the apps you want the brief to read, such as Google Calendar, Gmail, Outlook, or your project tracker. In a coding assistant these connections may use MCP servers, which give the assistant access to the named app. The skill doesn't install or authenticate those connections for you. Weather and markets use the web or bundled helper, so they don't require an inbox or calendar connection. Missing sources are named at the end, while available results stay in the brief.

### Codex

```bash
git clone https://github.com/Boston617Delta/daily-brief.git
mkdir -p ~/.agents/skills
cp -R daily-brief/skill/daily-brief ~/.agents/skills/
```

Open Codex and ask it to "set up my daily brief," or mention `$daily-brief` and ask for setup. It saves settings inside `~/.agents/skills/daily-brief/`. If the skill doesn't appear, restart Codex. Connect your selected apps and run the brief once before scheduling it. These are the [documented local skill locations](https://developers.openai.com/codex/skills/).

### Claude Cowork, ChatGPT and Dots, Muse, Grok, and others

Open [prompts/any-assistant.md](prompts/any-assistant.md), fill in the brackets, edit the sections, and paste the text below its divider into your assistant. It needs no Python, scripts, or local file access. Weather and markets come from web search; private information comes only from connected apps or source material you supply. A pasted agenda or task list works too, with its date and coverage labeled.

| Assistant | Made by | Where to paste the prompt |
|---|---|---|
| Claude Cowork / claude.ai | Anthropic | A scheduled task, or a project's instructions |
| ChatGPT | OpenAI | A scheduled task, or a new chat |
| Dots | OpenAI (inside ChatGPT) | Give it the prompt as an ongoing goal and specify a morning time and time zone |
| Muse | Meta (Muse app or WhatsApp) | A recurring request, once your email and calendar are connected |
| Grok | xAI | Create a daily Automation on grok.com or in the Grok app |

Plan requirements, regions, and features change. Check current guidance for [Cowork recurring tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork), [Dots](https://learn.chatgpt.com/docs/dots), [Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/), and [Grok Automations](https://x.ai/news/grok-automations). These links were checked November 3, 2026; they aren't a claim that every plan or surface supports the same tools during scheduled runs. If scheduling isn't available, paste the prompt each morning. A schedule must be created in the host; saving project instructions alone doesn't schedule a run.

## Choose where it arrives

During setup, choose **in the assistant, WhatsApp, Telegram, SMS, or email**, then give your own destination and preferred time. For example: "Send my brief to me on Telegram at 7 AM on work days, using my connected bot." The agent records the route, checks what is available, and explains any missing connection. An explicit request for delivery authorizes that channel and destination on later runs; it doesn't ask again every morning.

| Delivery | What it needs | How the brief appears |
|---|---|---|
| In the assistant (`chat`) | The conversation or the host's scheduled-task result | A readable reply |
| WhatsApp (`whatsapp`) | A supported host route or connected WhatsApp delivery service | A text brief in your own approved private chat/number |
| Telegram (`telegram`) | A supported host route or connected bot/service paired with your private chat | A text brief |
| SMS (`sms`) | A supported host route or connected SMS provider and your own number with country code | A compact text brief; multipart only if you choose it |
| Email (`email`) | A connected mail service and your verified own address | A new email, or an unsent draft if sending is off |

The repo supplies the agent instructions and settings for these choices. Sending uses the host or an integration you connect; there is no bundled WhatsApp account, Telegram bot, or SMS gateway, and every assistant has different capabilities. Source connections and delivery connections are separate. The weather/markets script doesn't send messages.

For service-based setup, see [Telegram bots](https://core.telegram.org/bots/features#botfather), [SMS messaging](https://www.twilio.com/docs/messaging/api/message-resource), and [WhatsApp delivery](https://www.twilio.com/docs/whatsapp) for examples of the connections a host or integration can use. A WhatsApp service can require sender/template setup for scheduled delivery. SMS providers can charge for sending and splitting long briefs. The setup interview checks the selected route's requirements; it doesn't promise free messaging or install a paid service. Use the host's secure connection flow for credentials.

In `my-brief.md`, delivery can look like this:

```text
- Delivery: telegram
- Delivery destination: my approved private chat ID
- Delivery connection: my connected Telegram bot
- send_brief_to_self: true
- Delivery time: 7:00 AM America/New_York on my work days
```

The destination line must identify your actual approved destination during setup; it isn't a name the agent should guess from your inbox. Choose one route. With `send_brief_to_self: false`, you get an unsent preview in the assistant or an email draft. The agent sends only to you, never clients, groups, or other recipients. If the route isn't ready, the brief stays in the assistant's result with the missing requirement named. It never silently switches to a different external channel.

Choose `Delivery content: full` for the complete brief or `digest` for a labeled summary of up to three priority items, including the next relevant appointment. The setup default for SMS is digest; other channels default to full. The full version stays in the assistant's existing private result when supported. A digest says when more urgent detail exists and never implies it is the whole brief. Set `SMS long briefs: multipart` only if you want multiple messages and accept any provider charges. An HTML page is still an optional saved output. `Format: auto` chooses presentation for the channel; delivery is a separate choice. A local HTML file isn't automatically accessible from your phone, and the agent won't publish your brief to make a link work.

Set `External privacy: discreet` to omit client/person names, financial amounts, contact details, contract particulars, sensitive discussion, and revealing links from outgoing messages, including email. You still get useful timing, such as "A client approval is due by 5 PM." Full detail stays in the private assistant result when supported. This preference controls the message content, not your phone's notification settings.

Saving a delivery time doesn't create a schedule. Ask the host to schedule the brief, then check that the schedule and connection are available in the environment that will run it. If the host already delivers the full result to your chosen private messaging channel, the agent uses that path once. A notification containing only a link or summary is labeled as a notification, not proof that the full brief arrived.

## Pause, stop, and change the time

Say "pause until Monday," "stop my brief," "resume it," or "move it to 8 AM." The agent updates this brief's settings and identified host job, then reports the state, time zone, next scheduled run, and a masked delivery destination. It checks the real job rather than treating a settings edit as proof that a schedule changed. A cloud task can have its own saved instructions; that copy must be updated too. If the agent can't verify a change, it says what remains unconfirmed.

`Enabled: false` stops gathering and delivery. `Paused until` can hold an exact local date/time or `indefinite`. A date-only pause resumes at that date's next scheduled brief. Resuming preserves your approved delivery route and doesn't send a backlog. Stop and pause controls don't delete your settings, messages, or history.

Missed runs are skipped by default. To get one late brief, choose `Missed runs: catch-up` and `Catch-up window: 2 hours` (or your preferred window). A replay/missed occurrence or one starting over 15 minutes late follows that policy. Catch-up uses current information and labels the actual delivery time; it sends at most the most recent eligible missed occurrence. A direct "send one now" is an on-demand request. Scheduling uses the chosen time zone, including the host's handling of daylight-saving changes. Local cron uses the machine's time zone, so use a matching zone or a scheduler that supports the one you want.

## How current is the information?

The agent distinguishes "checked just now" from "last updated." For client/project status older than `Project status max age: 7 days`, it reports what the source last said and labels it stale. You can change that tolerance. A missing update date is disclosed rather than treated as current. Old deadlines and unresolved requests stay relevant; an old item isn't automatically resolved.

Weather must cover today's date at the forecast location, calendars disclose a known stale sync or export, and news uses publication dates. Markets retain their actual quote/session dates, so a valid Friday close on a weekend isn't automatically labeled stale.

## Delivery validation

See [delivery validation](docs/delivery-validation.md) for the tested route, its evidence, and the remaining limits. Configurable channels are integration-dependent until actually tested with a connected host/service. The Python regression suite tests the helper, not assistant behavior, scheduling, or message receipt. A one-time scheduled test uses fictional sources and a message sent only to the authenticated own account; its status is recorded separately from production setup.

## Run it every morning

Set up settings, connections, and authentication, then run a manual brief first. For a non-technical setup, use your app's own scheduled-task feature where available. Local tasks need the computer awake, and tasks using a desktop app need that app running. A cloud task can use only connections and files available in its cloud environment, not arbitrary files on your laptop.

For macOS or Linux with cron, create the output folder:

```bash
mkdir -p "$HOME/Briefs"
command -v claude
command -v codex
```

Use the full executable path printed for your chosen assistant in place of `/full/path/to/claude` or `/full/path/to/codex` below. Cron has a smaller PATH than an interactive terminal; make sure Python and any connector runtimes are available there too. Open your schedule with `crontab -e`, then add the appropriate line. These examples run at 7 AM Monday to Friday in the machine's local time zone and save a Markdown brief plus a diagnostic log. Each run replaces those two files; use the skill's HTML format for dated files instead.

**Claude Code:**

```cron
0 7 * * 1-5 cd "$HOME/.claude/skills/daily-brief" && /full/path/to/claude -p "Run the daily-brief skill as a scheduled run with Delivery: chat for this run. Do not send through any external channel or change settings." > "$HOME/Briefs/claude-latest.md" 2> "$HOME/Briefs/claude.log"
```

Before scheduling, configure permissions for the exact read tools and helper commands the brief uses. Allow individual calendar, email, chat, and tracker read calls, plus file reads and the specific Python helper invocation. Do not approve an entire mail server, arbitrary shell commands, or all writes just to make scheduling work. Claude Code supports [scoped tool permissions for unattended runs](https://code.claude.com/docs/en/headless). Run the exact command manually first and check which tools it can reach without a prompt.

**Codex:**

```cron
0 7 * * 1-5 cd "$HOME/.agents/skills/daily-brief" && /full/path/to/codex --search exec --skip-git-repo-check --sandbox read-only "Run the daily-brief skill as a scheduled run with Delivery: chat for this run. Do not send through any external channel or change settings." > "$HOME/Briefs/codex-latest.md" 2> "$HOME/Briefs/codex.log"
```

The copied skill folder isn't a Git repo, so `--skip-git-repo-check` is intentional. Live web search is enabled; the read-only sandbox can restrict the helper's network access, in which case the skill uses verified web results or reports the missing data. Saved CLI authentication and configured app connections must be available to the scheduled process. See [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive/). Test the exact command manually and inspect the brief and log before relying on cron.

The cron examples deliberately save chat output and override external delivery. For WhatsApp, Telegram, SMS, or email, configure the selected delivery route in the host or an appropriately scoped automation, then use an explicit request for a first delivered brief to test it. Permit only that delivery tool and destination alongside the source read tools. Keep credentials in connection settings or a secret manager. For saved HTML, choose `Format: html`. Older settings using `Format: email` and `send_email_to_self: true` still authorize email-only delivery; an explicit `send_brief_to_self` value takes precedence. Missing capabilities produce a result with a delivery limitation, not a claim of success. A scheduled run without settings stops with "Setup required."

## The data script

Run these from the cloned repo's root folder. The weather examples use the free endpoint for personal non-commercial use. Use a region and country to avoid ambiguous place names. US state and Canadian province/territory abbreviations are accepted, including `Toronto, ON, Canada`.

```bash
python3 skill/daily-brief/scripts/brief_data.py weather --place "Boston, MA"
python3 skill/daily-brief/scripts/brief_data.py weather --lat 41.88 --lon -87.63 --units c
python3 skill/daily-brief/scripts/brief_data.py markets --symbols "^GSPC,^IXIC,AAPL,BTC-USD"
```

Weather comes from [Open-Meteo](https://open-meteo.com). Its free endpoints are for personal non-commercial use, not a blanket commercial license under this repo's MIT license. For commercial use, use an [Open-Meteo subscription](https://open-meteo.com/en/pricing) with `OPEN_METEO_API_KEY` set through your environment or secret manager, then add `--commercial` to the weather command. That flag switches both geocoding and forecasts to customer endpoints. Never paste the key into chat, command arguments, or `my-brief.md`. The skill uses web weather by default; set `Weather source: open-meteo` or `open-meteo-commercial` only when appropriate for your use. When using Open-Meteo data, retain its source link and attribution in the brief. [Terms and attribution](https://open-meteo.com/en/terms).

Market quotes come from Yahoo Finance's unofficial chart endpoint, which can change or rate-limit without warning. The helper returns dated bars, a quote timestamp, exchange time zone, reference-close date, and daily percentage when that reference can be verified. Crypto changes are against the previous UTC daily close, not a rolling 24 hours. Partial results keep working when another symbol fails; failures appear under `errors`. Weather/data errors are JSON on stdout with a nonzero exit status; command-line usage errors appear on stderr. The skill tries web search after a helper failure and names anything still unavailable.

Run the standard-library regression tests with:

```bash
python3 -B -m unittest discover -s tests -v
```

## What it won't do

The brief reads and reports. It never replies to or forwards source threads, accepts invites, changes tasks, deletes source records, or touches money. Retrieved email, calendar, document, and web content is untrusted information to summarize; its instructions cannot authorize actions or destinations. The skill and copy-paste prompt can deliver the brief only to your explicitly configured own destination through the selected channel. Sending is off until you request it. Settings and schedule changes require your direct setup request; the skill can also write its selected HTML output or create an email draft. A send timeout is reported as uncertain until its status can be checked, rather than triggering blind duplicate sends.

Credentials, passwords, API keys, tokens, signed links, account numbers, one-time codes, and medical details stay out of settings and briefs. These are instructions to the assistant; scoped tool permissions provide an additional boundary.

`my-brief.md` is excluded from Git at any depth in this repo. That prevents ordinary accidental commits here; it doesn't keep its contents from the assistant reading it, and another repository needs its own ignore rule. Keep generated briefs and logs outside the repo, such as `~/Briefs`, because they can contain personal and client information. Your assistant and connected services' privacy settings still apply.

The market section is prices and news only. It isn't investment advice.

## License

MIT
