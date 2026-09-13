# Runbook — the Wi-Fi flap that kills MCP, sends and uploads

**Diagnosed:** 2026-09-12, 17:40–18:20 local. **Host:** this Mac (Darwin 25.6), Wi-Fi `en0`.
**Verdict:** the link, not Desktop Commander, not the ISP, not Anthropic. Re-installing the plugin
changes nothing — the MCP server answers; the channel that carries the calls to it dies.
**Read the CORRECTION section at the bottom before using any number in this file**: the first-pass
mechanism (band flips cause the outages) was adversarially refuted and the causal arrow reversed.

## The symptom chain

The Mac keeps re-associating between the router's two radios under one shared SSID:
5 GHz **channel 112 (DFS)** ↔ 2.4 GHz **channel 11**. Every transition fires a full macOS
network-configuration change, and every long-lived connection dies with it:

| layer | what the operator sees |
|---|---|
| Claude Desktop ↔ cloud (`remote-tools-device` WebSocket) | Desktop Commander tool calls hang, then `notifications/cancelled` |
| chat POST | «Failed to send» |
| upload | «Upload failed due to a network issue» |
| streaming API from the terminal | `Connection lost mid-response` |

## Evidence (all measured, nothing typed)

**Topology.** `en0` = 192.168.2.52/24 · gateway 192.168.2.1 = Telekom Speedport
(`search domain speedport.ip`, MAC `dc:92:72:60:3c:4c`) · sole nameserver = the router.

**No IPv6 at all** — only `fe80` link-local on every interface; `curl -6 https://claude.ai` came back
as `::ffff:160.79.104.10` (v4-mapped) and `airportd` logs `ipv6Primary=no`. Any «half-broken IPv6»
theory is dead: there is no IPv6 to break.

**DNS is not the fault.** 24 distinct names against 192.168.2.1, 1.1.1.1 and 9.9.9.9 → `1/24` failed
on *each* resolver, and it was the same name every time (`statsig.anthropic.com`, no A record).
The `ERR_NAME_NOT_RESOLVED` in the app log is collateral: lookups in flight when the link changes.

**The band flip, caught live.** Sampling the channel every 6 s:

```
sample 1-9 : Channel 112 (5GHz, 80MHz)  RSSI -38..-41 dBm
sample 10+ : Channel  11 (2GHz, 20MHz)  RSSI -50..-56 dBm  TxRate 0/17/25 Mbps
```

**The blackout, confirmed on TCP** (so not an ICMP-policing artifact). `curl time_connect`, one
sample per ~4 s, gateway:80 and api.anthropic.com:443:

```
18:12:41  gw=0.0056  api=0.0165  ch=11      healthy
18:12:45  gw=FAIL    api=0.716   ch=11
18:12:52  gw=FAIL    api=0.408   ch=11
18:12:58  gw=1.469   api=0.019   ch=11
18:13:03  gw=FAIL    api=4.650   ch=112     <- flip to 5 GHz
18:13:13  gw=FAIL    api=FAIL    ch=112
18:13:20  gw=FAIL    api=FAIL    ch=11      <- flip back
18:13:23 .. 18:13:34  gw=FAIL api=FAIL      6 consecutive samples
18:13:37  gw=2.583   api=FAIL    ch=11
18:13:44  gw=0.0063  api=0.0167  ch=11      recovered, clean until 18:16:33
```

~60 s of total blackout, and **the gateway on the LAN is unreachable too** — that is what rules out
the ISP and Anthropic.

**Packet loss, same windows.** gateway 60 pkts @0.2 s → **73.3 %** loss, max RTT **1718 ms**;
1.1.1.1 in the same window → 93.3 %; gateway 60 pkts @0.5 s while on ch 11 → **83.3 %**, max RTT
1110 ms. Between bursts: 200 pkts over 100 s → ~0 %. So it is bursty, not degraded-always — and the
signal is excellent throughout (−38…−56 dBm, SNR 35, CCA 20 %), so it is not range and not noise.

**System log, 6 h window** (`/usr/bin/log show --last 6h --style compact`, 7 987 712 lines):

```
1259  ROAM_MANAGER_EVENT_ROAM_START        (bursting 10-14 per MINUTE in bad stretches)
 160  "Associated on DFS channel 112"
 176  "Associated on non-DFS channel 11"
 482  LINK_DOWN   /  188 EVENT_LINK_DOWN  /  243 EVENT_LINK_UP
 configd "IPMonitor] network changed" per hour: 19(12h) 1(13h) 53(14h) 21(16h) 51(17h) 4(18h)
```

The cascade in full, one flip:

```
18:09:21 kernel  : Associated on non-DFS channel 11 (40MHz+)
18:09:40 configd : network changed: v4(en0!:192.168.2.52) DNS+ Proxy+ SMB
18:09:40 kernel  : FSM ROAM_MANAGER: LINK_UP -> ROAM_START -> ROAM_SCAN -> ROAM_DONE
18:09:40 …       : "PrimaryNetwork changed" / "received network changed event" to every daemon
18:09:43 airportd: REACHABILITY [reachable=yes, ipv4Primary=yes, ipv6Primary=no]
```

**Desktop Commander is innocent.** `~/Library/Logs/Claude/mcp-server-Desktop Commander.log` shows the
server returning results normally; the *client* sends `notifications/cancelled` after ~4 min. No
server-side error anywhere in it.

**Also present, secondary:** 8 `utun` interfaces and two configured VPN network services —
`OpenVPN TCP (com.free.vpn.usa.planet)` and Tailscale — with no process running. Not the cause of the
band flips, but they add `network changed` churn and a free-VPN service in the service order is worth
removing on its own merits.

**Neighbour scan** (why 2.4 GHz is a bad fallback here): 2.4 GHz — 5 APs on ch 1, 3 on ch 6, 1 on
ch 7, 2 on ch 11. 5 GHz — 2 APs on ch 36, 2 on ch 112, 1 on ch 136.

## Method notes (cost me time — read before re-running)

- `log` is shadowed by a shell function from the user's profile: `log show …` dies with
  `(eval):log:1: too many arguments`. Use **`/usr/bin/log`**.
- **zsh does not word-split an unquoted variable**: `for n in $names` runs *once* over the whole
  string. Use an array and `"${names[@]}"`. (Cost one void DNS test here.)
- Ping alone is not proof: routers rate-limit ICMP to their own address. Confirm every loss claim
  with a **TCP connect** to the same address.
- `system_profiler SPAirPortDataType` takes seconds and triggers a scan — do not treat it as a free
  probe, and do not let it be the only witness to a roam.
- macOS 26 has no `airport` binary; `wdutil info` and `profiles list` need root. SSID/BSSID come back
  `<redacted>` without privileges.

## The fix

Router-side, at `http://speedport.ip` (needs the device password on the router's sticker):

1. **Split the SSIDs** — give 2.4 GHz and 5 GHz different names / turn off band steering, then join
   the Mac to the 5 GHz one only. This alone stops the ping-pong.
2. **Pin the 5 GHz channel to a non-DFS one** (36/40/44/48) and switch off automatic channel choice,
   so the radio cannot wander back into the DFS range.
3. Reboot the router after applying.

Mac-side, immediate and no admin: Ethernet, or a phone hotspot, if a session must not be interrupted.

What *not* to do: re-install Desktop Commander, reset the MCP config, or switch DNS servers — the
evidence exonerates all three.


---

# CORRECTION (same session, after adversarial review)

Six agents were told to break the verdict above. The *premise* held; the *mechanism* did not. Three
of the headline numbers in this file are mis-parses and must not be reused.

## Numbers that were wrong

| claimed | actually |
|---|---|
| 160 + 176 "associations" on ch112 / ch11 | all 336 come from ONE kernel routine, `configureValidAWDLChannels:19115` — AWDL channel bookkeeping, **not association events** |
| 482 `LINK_DOWN` / 188 / 243 | token sums across three parallel state machines and across the `in state:` / `moved into:` positions of a single FSM line (`482 = NET_MANAGER 292 + ROAM_MANAGER 98 + …`) |
| 1259 `ROAM_START` = 1259 transitions | `ROAM_REASSOC` = 76, `CONNECT_COMPLETE` = 43 — ~94 % were scan-and-stay. Deduped: 179 association events, 98 real channel changes |

## What the evidence actually says

**macOS adjudicates its own failures, and it disagrees with the band-flip story.** The dump holds 142
`WiFiUsageLQMWindowAnalysis` reports. Across the 129 carrying flags:

```
band_hasChanged_inBefore    = 0   in 129/129
channel_hasChanged_inBefore = 0   in 129/129
sameBSSID                   = 1   in 113/129
triggers: DatapathStall 66 · SlowWiFiDnsFailure 46 · Join 16 · reason 13 · LinkDown 1
```

A band change is named **zero** times. The failures happen on an *unchanged* association.

**The loss is on the air interface, with no roam at all.** Concurrent ping 18:28:18→18:28:39: 60.0 %
loss to the gateway and 65.0 % to LAN peer 192.168.2.50, the *same* sequence numbers dropped on both.
A `log show` over exactly that window for roam / association / channel / network-change events returned
**zero rows** (control: the same predicate returns 26 rows over 18:17:00–18:17:30). LAN-peer ICMP never
touches the router's IP stack — so the failing hop is Mac ↔ AP, and no roam was involved.

**The Mac, not the router, decides to roam.** Zero 802.11v BSS-Transition requests, zero channel-switch
announcements in 6 h. Every roam is `Roam Scan Started by FW` — the Mac's own firmware — at RSSI −47…−59
dBm (mode −52, none below −60). "Band steering" mis-names the actor. And 22 % of roams are intra-band
same-BSSID, which no SSID split could touch.

**Some flips are consequences, not causes.** `SlowWiFiDnsFailure` *triggers* a roam (dampened by quota
274 times). Base-rate-corrected against the app's 177 real failure events: datapath stall lift 3.9×/2.0×,
any roam 3.4×/2.7×, **band transition only 2.5×/1.8×** — the weakest of the three. 88 % of app failures
have no band transition within 5 s.

**The mechanism that fits: a transmit-queue stall in the Mac's Wi-Fi datapath.**

```
423 x kernel: "Datapath timeout on en0 for AC N with interface CCA X%, which has NNN remaining pending packets"
  per hour: 141 (14h) · 107 (16h) · 174 (17h) · 1 (18h) · zero in 12h/13h/15h  -> bursty by the hour
  queue depth: n=423, median 224, p90 576, max 767 pending packets
  mostly AC=0 (best effort), CCA 10-37%  -> the CHANNEL WAS IDLE
  retry storm on a pristine unchanged ch112 association at RSSI -41:
    txFrames/txReTx  86/25 -> 245/43 -> 174/38 -> 183/101 -> 210/880 -> 519/1157
```

519 frames against 1157 retransmissions, at −41 dBm, on an idle channel. That is not range, not noise,
not congestion.

**A correlation that does NOT hold — recorded so nobody re-derives it.** AWDL looked like the culprit
(AirDrop/Continuity time-sharing the radio). It is not supported: `awdl0` appears in 20 886 distinct
seconds of the ~21 600-second window, so the 175/177 same-second overlap with datapath timeouts is
exactly what chance predicts. No signal. Base-rate the denominator before believing any overlap here.

## What was changed on the router (2026-09-12 ~18:29)

`http://speedport.ip` → Netzwerk → WLAN-Einstellungen → Sendeeinstellungen → 5-GHz-Frequenzband →
**Kanal: "Automatisch" → "Kanäle 36, 40, 44, 48"**. One field. Width (80 MHz), mode (802.11n/ac/ax),
2.4 GHz settings and both SSIDs untouched. The Speedport offers only three fixed 80 MHz blocks and
36/40/44/48 is the only non-DFS one.

Router status before the change confirmed the premise independently of any macOS reading:

```
WLAN 2,4 GHz : Kanal 11 (Automatisch)                  SSID MagentaWLAN-0E8J   Geräte 0
WLAN 5 GHz   : Kanal 100, 104, 108, 112 (Automatisch)  SSID MagentaWLAN-0E8J   Geräte 6
DSL: 113,3 / 40,53 Mbit/s, Internetverbindung aktiv seit 30.07.2026  -> no WAN resync, ISP clean
```

Topology, recovered from unredacted `WiFiUsageLQMWindowAnalysis` blobs (airportd redacts, these do not):
gateway LAN MAC `dc:92:72:60:3c:4c`, BSSIDs `…:4e` (ch11) and `…:4f` (ch112) — three consecutive MACs
in one OUI block = **one box, two radios**. No repeater, no mesh (`isFTactive=0` in all 258 occurrences).

## Effect of the change — real but NOT yet proof

| | before | after |
|---|---|---|
| TCP sampler, 60 samples | 12 FAIL, one ~60 s total blackout | **0 FAIL**, channel never moved |
| `Datapath timeout on en0` | 423 in 6 h | 0 in the first ~12 min |
| Mac PHY | ch112 80 MHz, 432 Mbit/s → ch11 20 MHz, 17–25 Mbit/s | **ch36 80 MHz, 1200 Mbit/s**, steady |
| deduped roams | 91 in the 40 min before | 3 in the 12 min after, all on ch36 |

**Why this is not yet proof — the power calculation.** The 423 timeouts span 14:10:15 → 18:07:50
(none at all before 14:10 today). Gaps between consecutive timeouts, pre-change:

```
longest    88.8 min   (14:50:50 -> 16:19:35)
2nd        41.8 min
3rd        18.2 min      median gap 0.0 min (they come in dense bursts)
4th        14.2 min      gaps > 14 min: 4
```

**So a quiet run only becomes evidence past ~90 minutes.** Fifteen minutes of silence is deep inside
the natural gap and proves nothing. No watcher is needed to settle this — the counter is retrospective:

```
/usr/bin/log show --start '2026-09-12 18:30:00' | grep -c 'Datapath timeout on en0'
```

Read it after 20:00 local (90+ min post-change). Zero then is real evidence; anything above zero
means the change did not address the fault. And Claude Desktop
still logged `ERR_INTERNET_DISCONNECTED` at 18:31:24–27 and `socket closed: 1006` at 18:37:01, after the
change (the 18:31 cluster is plausibly the radio restart the change itself caused; 18:37 is not).

The 18:37:01 close has **no radio event behind it**: a log query over 18:36:46–18:37:16 for roam /
association / datapath-timeout / link-down / network-change returned only routine LQM statistics
(control: the same predicate returns 228 rows over the busy 18:17:00–18:17:30). The link was clean at
that moment — `rssi=-50 noise=-90 snr=34 cca=5.0% rxPER 0% txRTSFail=0`. So that one is app- or
server-side, not the network: the app layer has a second source of 1006s, and not every socket close
in `main.log` is evidence of a link fault.

Keep the change — it removes DFS radar evacuation as a failure mode at zero cost, and the PHY rate
tripled. But do not call it the root fix until the test below runs.

## The one test that settles it

**Put the Mac on a completely different AP — a phone hotspot on 5 GHz — for ~30 minutes** and re-run
the TCP sampler plus `Datapath timeout on en0` counting.

- stalls FOLLOW the Mac onto the hotspot → the fault is the Mac's Wi-Fi chain (driver, chip, or an OS
  interaction); the router change is cosmetic and the next step is Mac-side.
- stalls STOP on the hotspot → the fault is the Speedport's AP path for this client; next step is
  Speedport firmware / a different AP.

Both surviving readings predict identical logs on the current AP, so only this swap separates them.
Ethernet through the same Speedport for 30 min is a useful second control: same ISP, same router, no
Wi-Fi.

## Standing conclusion (unchanged by the correction)

Desktop Commander, its config, the MCP layer, DNS and the ISP are all exonerated. The failure is the
Mac ↔ Speedport air link dropping traffic in bursts while associated. Do not reinstall the plugin.
