# Real-time meeting avatar bridge

Ourogen keeps the meeting agent's reasoning, consent flow, and ElevenLabs voice in the main backend. A small
media worker turns that existing audio into lip-synced Tavus video and exposes it to Recall as Output Media.
This avoids running a second conversational agent and prevents duplicate voices.

The feature is off unless both `MEETING_AVATAR_BRIDGE_URL` and `MEETING_AVATAR_BRIDGE_SECRET` are set. If the
worker is unavailable, the call automatically uses Recall audio and the user's verified static avatar.

## Worker contract

All requests use `Authorization: Bearer <MEETING_AVATAR_BRIDGE_SECRET>`.

- `POST /sessions` accepts `meeting_id`, `user_id`, `display_name`, `replica_id`, and a `greeting` containing
  `text` and optional `mp3_b64`. It returns `{"id": "...", "camera_url": "https://..."}`. The camera URL must
  be short-lived and HTTPS. The worker should queue the greeting until Recall opens the page.
- `POST /sessions/{id}/speak` accepts `mp3_b64` and `text`. Feed the supplied audio into Tavus's audio
  passthrough pipeline; do not synthesize another voice.
- `POST /sessions/{id}/stop` immediately clears queued and playing audio for barge-in.
- `DELETE /sessions/{id}` closes vendor sessions and releases media resources.

The camera page is passed to Recall's `output_media.camera` on the `web_4_core` bot variant. It must render the
Tavus video and its synchronized audio without requiring a browser login or exposing the bridge bearer secret.
Use a signed, expiring token in the camera URL and reject replay after the session closes.

## Production configuration

Add these to the same production secret/environment source used by the backend and then redeploy:

```dotenv
MEETING_AVATAR_BRIDGE_URL=https://meeting-avatar.ourogen.ai
MEETING_AVATAR_BRIDGE_SECRET=<random 32-byte-or-longer secret>
```

The worker separately needs `TAVUS_API_KEY` and `TAVUS_REPLICA_ID`. Ourogen's backend continues to own
`ELEVENLABS_API_KEY` so there is only one TTS source.
