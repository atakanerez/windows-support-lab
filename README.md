# Windows Support Lab: DNS and Active Directory

A support case study and offline Python tool for reviewing DNS and domain
controller discovery checks. All observations are synthetic. This project
does not query live systems and does not claim that a Windows Server or
Active Directory environment was deployed.

## Incident

A Windows client reportedly cannot locate a domain controller for the
fictional domain `corp.example`. In the initial record, the client uses a
resolver that differs from the lab baseline. DNS cannot resolve the domain
controller SRV record and controller discovery fails.

| Step | Windows check | What to record |
| --- | --- | --- |
| Client configuration | `ipconfig /all` | Does the client use the expected internal DNS resolver? |
| DNS service discovery | `Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.corp.example` | Does the domain controller SRV query return a record? |
| Controller discovery | `nltest /dsgetdc:corp.example /force` | Does the Windows client locate a controller? |

In the walkthrough, the technician restores the approved lab resolver
configuration and repeats the same checks. The synthetic follow-up record
shows successful SRV lookup and controller discovery. Sign-in and access
to the affected application are separate verification steps; this tool
does not report that either succeeded.

## Run the sample

Python 3.10 or later; no dependencies.

```sh
python3 diagnose.py before.json
python3 diagnose.py after.json
python3 -m unittest -v
```

## Example output

```text
check_client_dns: Verify the configured DNS resolver against the lab baseline, then repeat the checks.
discovery_restored: Domain controller discovery succeeded; verify user sign-in separately.
```

Each JSON field records the observed result of one check in the table,
in order: `client_dns_matches_lab`, `dc_srv_resolves`, and
`domain_controller_discovery`. Use JSON booleans. The tool suggests the
next check when discovery fails; it does not assert a root cause from a
single result. Invalid input exits with status 2.

## Verification results

**16 November 2026** · Clean checkout of [`3139e84`](https://github.com/atakanerez/windows-support-lab/commit/3139e84) · Linux, Python 3.12.14. All **5 unit tests** and **6 command-line checks** passed using synthetic inputs.

| Command-line scenario | Observed output code | Exit |
| --- | --- | --- |
| Client resolver differs from the baseline; SRV lookup fails | `check_client_dns` | 0 |
| Client resolver matches the baseline; SRV lookup fails | `check_srv_resolution` | 0 |
| SRV lookup succeeds; controller discovery fails | `check_dc_discovery` | 0 |
| SRV lookup and controller discovery succeed | `discovery_restored` | 0 |
| A check result is a string rather than a boolean | Input error on stderr; no stdout | 2 |
| Malformed JSON | Input error on stderr; no stdout | 2 |

### Live Windows and Active Directory validation — pending

Requires an isolated Windows Server lab with AD DS and DNS, a domain-joined Windows client, and a dedicated test account. Capture the three checks in the incident table before and after correcting the client DNS setting. Pass criteria: the client uses the approved lab resolver, the SRV lookup returns the expected controller, controller discovery succeeds, and a fresh sign-in with the test account is confirmed against the domain rather than relying on cached credentials. Retain only redacted evidence.

The Python results above validate the offline tool. Windows commands and domain sign-in have not been run in a live lab.
