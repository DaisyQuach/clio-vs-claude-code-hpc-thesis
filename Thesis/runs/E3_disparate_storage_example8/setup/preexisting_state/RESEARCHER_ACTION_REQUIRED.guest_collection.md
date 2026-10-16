# RESEARCHER ACTION REQUIRED — create the E3 guest collection in the Globus web app (Phase 2.4)

Date: 2026-10-10 UTC. Status in `setup/E3_BLOCKER_STATUS.yaml`. E3 is **NO-GO**. Earlier instructions are kept in
`setup/preexisting_state/RESEARCHER_ACTION_REQUIRED.{globus_login,gcs_consent}.md`.

## Why the CLI cannot do this
The host collection *University of Utah -- CHPC DMZ Clustered Endpoint* (`7cf0baa1-8bd0-4e91-a1e6-c19042952a7c`)
allows guest collections (`shareable: true`). It is high-assurance, with a one-year authentication timeout.

Creating a guest collection has to talk to the endpoint's Globus Connect Server manager, `https://264d8.75bc.data.globus.org`.
From login node notchpeak1, TCP port 443 to that server (204.99.128.85–88) times out. The transfer API and `globus ls`
work. Nothing was created, and no token or code was handled.

## Your action (Globus web app, in your own browser)
1. Open https://app.globus.org and sign in with your University of Utah identity.
2. In **File Manager**, set Collection to **University of Utah -- CHPC DMZ Clustered Endpoint**. Set Path to
   `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/globus_source_root/`
   You should see `documentation/ manuals/ target_materials/ MANIFEST.sha256 MANIFEST.tsv README.md`.
3. Click **Share** in the right-hand panel, then **Add Guest Collection**.
   - **Path:** exactly the directory above. Do not use a parent such as `E3_disparate_storage_example8/`, which would
     expose `researcher_only/` and `setup/`.
   - **Display Name:** `daisy-e3-private-source`
   - **Description:** `E3 private read-only source collection (researcher only)`
   - Click **Create Guest Collection**.
4. On the new collection's **Permissions** tab, add **no** permissions: no users, no groups, never "all users" or
   "public". Leave only your own access as owner.
5. Copy the collection **UUID** from its Overview page. The UUID is an identifier, not a secret.

If **Share** or **Add Guest Collection** is unavailable or gives a policy error, stop and send CHPC this request
(helpdesk@chpc.utah.edu):
> Subject: Globus guest collection on CHPC DMZ Clustered Endpoint for a private read-only research directory
>
> I need a private Globus guest collection, shared with no one but me, rooted at
> /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/globus_source_root on the
> "University of Utah -- CHPC DMZ Clustered Endpoint" (7cf0baa1-8bd0-4e91-a1e6-c19042952a7c). Creating it failed with:
> <paste the error text>. Could you enable it or create it for me?
>
> Also, from login node notchpeak1, TCP 443 to the endpoint's GCS manager (264d8.75bc.data.globus.org) and to its HTTPS
> server (m-78bbc5.264d8.75bc.data.globus.org) times out. Is that expected, and can compute nodes on the hochhalter-np
> partition reach the Globus transfer API (transfer.api.globus.org) noninteractively?

## Verify afterwards (safe, read-only)
```bash
module load python/3.12.4
G=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus
$G ls <UUID>:/
```
Expected: the six entries above, and nothing from outside `globus_source_root/`.

## Then send
> Guest collection created: <UUID>. Resume E3 readiness.

## Still pending from you
The CLIO deployment choice for Phase 5: local CLIO Desktop connected to CHPC, or a documented remote/headless runner.
