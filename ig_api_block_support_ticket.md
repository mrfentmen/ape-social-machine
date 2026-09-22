# Meta Developer Support — Instagram API blocked (App ID 2056380568328230)

Paste this into https://developers.facebook.com/support (or email it as-is).
Fill in the two `[...]` blanks before sending. Trace ids are from 2026-09-19 and expire, so send soon.

**Subject:** Instagram API access blocked (OAuthException code 200) and app cannot be validated — App ID 2056380568328230

---

Hello Meta Developer Support,

Our Instagram API integration is fully blocked and we cannot find any alert, violation, review, or appeal path in any dashboard. We need help identifying and removing the restriction.

**App**
- Instagram App ID: `2056380568328230`
- App name: [name shown in the App Dashboard]
- Region: United States

**Instagram professional account**
- Username: `blitztheape`
- IG User ID: `17841434263231804`
- Account type: MEDIA_CREATOR
- Business portfolio: [portfolio name / ID, if shown in Business Settings]

**What happens**

Every Instagram API request fails, including read-only calls that require no permissions:

```
GET  /me?fields=id,username,account_type
     -> 400 {"error":{"message":"API access blocked.","type":"OAuthException","code":200,
              "fbtrace_id":"AeYsPeK-hd91pu2uXLeXNW1"}}

GET  /17841434263231804?fields=username,account_type,media_count
     -> 400 {"message":"API access blocked.","type":"OAuthException","code":200}

GET  /17841434263231804/content_publishing_limit?fields=config,quota_usage
     -> 400 {"message":"API access blocked.","type":"OAuthException","code":200}

GET  /17841434263231804/media?fields=id,timestamp,media_type
     -> 400 {"message":"API access blocked.","type":"OAuthException","code":200}

GET  /refresh_access_token?grant_type=ig_refresh_token
     -> 400 {"message":"API access blocked.","type":"OAuthException","code":200,
              "fbtrace_id":"ARYwlNwmXUq_OkGxvmTOzms"}
```

Host: `graph.instagram.com`.

**The app itself also fails to validate.** Using the App ID and App Secret directly:

```
GET  /v21.0/2056380568328230?fields=name   (app access token)
     -> 400 {"message":"Error validating application. Cannot get application info due to a
              system error.","type":"OAuthException","code":190,
              "fbtrace_id":"ARteARXa-Ghwx0eEMQiUxjp"}

POST /v21.0/oauth/access_token  (grant_type=client_credentials)
     -> 400 {"message":"Error validating application. Cannot get application info due to a
              system error.","type":"OAuthException","code":101,
              "fbtrace_id":"Al-K1CrqepISynS5-vyMY99"}
```

Meta cannot read our own app record, which suggests the app is disabled or restricted rather than the token being bad.

**Timeline**

- Token issued: `2026-09-17T19:24:44Z` (long-lived Instagram user token, stored as GitHub Actions secret `IG_ACCESS_TOKEN`, still in place and unchanged)
- Last successful API publish: `2026-09-18T16:58:36Z`
- First observed refusal: `2026-09-19T14:02Z` from our scheduled cloud job
- Status now: still blocked, roughly 24 hours later

**What we have already checked**

- App Dashboard: no red "API access restricted" banner, Alerts Inbox shows nothing actionable, Required Actions page is empty
- Business Support Home: no restricted assets listed
- Account Quality: no violation shown for the Instagram account or the page
- No email, notification, or in-app message about a policy violation, token revocation, or app restriction
- Token and secret are unchanged since they were issued; we run one post scheduler and one scheduled reel every few hours

**Impact**

Our scheduled Instagram Reels publishing is completely stopped. On 2026-09-19, 83 posts were due and 0 published. The integration is broken for both publishing and reading.

**What we are asking**

1. Please identify the exact restriction causing `API access blocked.` (code 200) on App `2056380568328230`, and why the app cannot be validated (`Cannot get application info due to a system error`).
2. Please restore API access, or tell us the specific review or appeal path we should use.
3. If there is a required action on our side, please name it — nothing actionable is visible in any dashboard we have access to.

Additional trace ids from the same period if useful:
`A19hP4WfWcm9FYDsENgFhvk`, `Aoe2fA0fnrkLaxS4EBuerd4`, `A1gRCvrpqftphsnEI3Io_78`,
`AAAJyYAnfnOtKXsGU-kDihp`, `AtMS7pQNexRYGeCkbAKJ1tC`, `AjVhpmeh`, `AT3GnAXO`.

Thank you,
[your name]
[email address]
