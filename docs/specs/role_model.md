
| Capability | `user` | `power_user` | `partner` | `admin` |
|---|:--:|:--:|:--:|:--:|
| Submit an assessment for self | ✓ | ✓ | — | — |
| Read own reports | ✓ | ✓ | ✓ | — |
| Read all reports in own organization | — | ✓ | — | — |
| Read reports across assigned organizations | — | — | ✓ | — |
| **Read any report** | — | — | — | **MUST NOT** |
| Approve or send back a report | — | — | ✓ | — |
| Add users to an organization | — | — | ✓ | ✓ |
| Revoke an unconsumed invitation | — | — | ✓ own orgs | ✓ |
| Grant or revoke `power_user` | — | — | ✓ | — |
| Rename an organization | — | — | ✓ | ✓ |
| Re-send an invitation to a `user` / `power_user` | — | — | ✓ | ✓ |
| Suspend or restore a `user` / `power_user` | — | — | ✓ | ✓ |
| Create organizations | — | — | — | ✓ |
| Create partners and admins | — | — | — | ✓ |
| Link or unlink a partner to an organization | — | — | — | ✓ |
| Re-send an invitation to a `partner` / `admin` | — | — | — | ✓ |
| View mail delivery status for an invitation | — | — | ✓ own orgs | ✓ |
| Manage the mail suppression list | — | — | — | ✓ |
| **Obtain, set or view any authentication secret** | — | — | **MUST NOT** | **MUST NOT** |
| **Change the email address on a `partner` / `admin` account** | — | — | **MUST NOT** | **MUST NOT** |
| Read the audit log | — | — | — | ✓ |
| Manage e-mail templates | — | — | — | ✓ |
| Manage prompts | — | — | — | ✓ |
| Manage consents | — | — | — | ✓ |
| Manage application settings  | — | — | — | ✓ |