# Phase 0 checks (throwaway)

Scratch material for the security hardening plan's Phase 0. Never merged.

- **Check B** (dashboards under a content security policy): every template in
  `system/dashboards/` on this branch carries the policy meta tag. All 12
  render from the fixtures, open in Chromium with no console errors, and a
  planted outside request is blocked. Still to check: the artifact host.
- **Check A** (Cowork shows a hook's confirm prompt): `confirm-probe/` is a
  tiny standalone repo. Copy its `.claude/` folder into a new private repo in
  the test account, attach that repo to a new Cowork project, and in a chat
  ask Claude to run `echo confirmprobe`.
