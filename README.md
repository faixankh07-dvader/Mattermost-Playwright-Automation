# Mattermost test automation (Playwright + Python)

Automated regression tests for a self-hosted Mattermost, built from the manual test suite in
[Mattermost-Manual-QA](https://github.com/faixankh07-dvader/Mattermost-Manual-QA).
Every automated test carries the ID of the manual test case it covers, and
[`docs/traceability.md`](docs/traceability.md) maps all 71 manual cases to their automated tests.

**Status:** 30 of the 71 manual cases are automated by 49 pytest tests (35 UI, 14 API).
The generated traceability table is the source of truth if these numbers drift.

## Stack

- Python, pytest, pytest-playwright (Chromium), requests, python-dotenv
- Mattermost Enterprise Edition 11.7.0 with Postgres 18, run locally with Docker Compose at `http://localhost:8065`

## Project layout

```
.
├── conftest.py            fixtures: api, team, make_user, new_user, auth_state, admin_page, message_channel
├── pytest.ini             base_url, trace/screenshot on failure, the `tc` marker
├── requirements.txt
├── .env.example           copy to .env and fill in
├── docs/
│   ├── manual_cases.csv   all 71 manual cases (id, epic, title)
│   └── traceability.md    generated, do not edit by hand
├── pages/                 Page Objects: login, channel, message panel, search
├── scripts/traceability.py
├── tests/
│   ├── api/               REST-level tests: smoke, permissions, search, files
│   └── ui/                Playwright UI tests
└── utils/                 api_client.py (REST client), ui_auth.py (login), ui_popups.py
```

## Setup

### 1. Mattermost

Run Mattermost with Docker Compose and make sure the **Site URL is `http://localhost:8065`**
(for the official compose setup this is `MM_SERVICESETTINGS_SITEURL` in the compose `.env`).
With any other value the WebSocket handshake is rejected with HTTP 403 and the real-time tests fail
(see [Findings](#findings)).

The tests also expect:

- a system admin account and a team that already exist
- the default permission scheme (the permission tests depend on it)

### 2. This project

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env          # then edit .env
```

`.env` variables:

| Variable | Meaning |
|---|---|
| `MM_ADMIN_USER` | system admin username |
| `MM_ADMIN_PASS` | its password |
| `MM_TEAM` | URL name of the team the tests run in |

## Running the tests

```bash
pytest -v                                   # everything (about 7-8 minutes, runs serially)
pytest tests\api -v                         # REST-level tests only, a few seconds
pytest tests\ui\test_search.py -v           # one file
pytest -k logout -v                         # by name
pytest tests\ui -v --headed --slowmo 500    # watch the browser
pytest -v --html=reports\report.html --self-contained-html   # same, plus an HTML report
```

On failure, a screenshot and a trace are kept in `test-results/`.
Open a trace with `playwright show-trace test-results/<folder>/trace.zip`.
The HTML report is written to `reports\report.html` (git ignores it).

Regenerate the traceability table after adding or retagging tests:

```bash
python scripts/traceability.py
```

## How the tests are built

- **API for setup, UI for what is under test.** Users, channels, posts and files are created through the REST API, so a UI test only exercises the behaviour it is about.
- **Throwaway data.** Every test creates uniquely named users and channels. Teardown archives the channels and deactivates the users, and checks that the deactivation really happened.
- **One UI login per user.** `auth_state` logs a user in through the UI once and reuses the saved session.
- **Negative results are paired with a control.** Before asserting that something is hidden or forbidden, the test first shows that the same thing works for an allowed user, so a wrong locator or setup cannot make the test pass by accident. The real-time tests run a `live` and an `after-refresh` variant for the same reason.
- **No sleeps.** To prove that nothing happened (for example a rejected message), the test posts a sentinel message afterwards and waits for it.
- **Popups are handled by locator handlers.** New users get an onboarding overlay and Mattermost shows product-notice modals at unpredictable moments. Playwright locator handlers dismiss them when they block an action.
- **Locators** prefer roles and test ids, and are scoped to the element they belong to (for example the confirmation dialog, not the whole page).

## Findings

**Three apparent defects were an environment problem.** Two manual defect reports and a note on a third test case described the UI updating only after a manual refresh (new messages, a demoted Channel Admin still offered "Delete", unread state not syncing). I wrote the automated tests as expected failures first. DevTools then showed the WebSocket handshake failing with HTTP 403, and the Site URL still had the Docker default (`https://mm.example.com`) while the app was opened at `http://localhost:8065`. After correcting the Site URL the WebSocket connected (101), the same tests started passing, and the expected-failure markers were removed. The reports were closed as environment misconfiguration.

## Known limitations

- 30 of 71 manual cases are automated. Cases left out on purpose, with the reason, are noted in the traceability table (account lockout, email delivery, network interruption, server-wide settings).
- The API tests check the REST permission model. They do not replace the UI checks in the manual cases.
- T49 covers 3 of its 4 example inputs; the emoji example is not automated.
- T16: the browser back-button step stays a manual check.
- The suite assumes one local Mattermost instance and runs serially.

## Planned

- GitHub Actions run with Docker Compose
- Parallel execution

## Author

M Faizan Khan, [github.com/faixankh07-dvader](https://github.com/faixankh07-dvader)
