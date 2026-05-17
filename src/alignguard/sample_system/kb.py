"""Mock knowledge base for the CloudBase customer support sample system."""

KB: dict[str, str] = {
    "storage_plans": """\
CloudBase Storage Plans:
- Free: 5 GB, 1 user, community support
- Basic ($9.99/mo): 100 GB, 3 users, email support
- Professional ($29.99/mo): 1 TB, 10 users, priority support, version history
- Enterprise (custom pricing): unlimited storage, SLA guarantee, dedicated CSM

Upgrades take effect immediately and are prorated.
Downgrades apply at the start of the next billing cycle.""",

    "refund_policy": """\
CloudBase Refund Policy:
- Refund requests must be submitted within 30 days of the charge date.
- Pro-rated refunds are available for annual plans (unused months only).
- No refund if more than 10 GB was downloaded in that billing period.
- Process: submit support ticket → 2-3 business day review → credit to original
  payment method within 5-7 business days.
- For disputed charges contact billing@cloudbase.io with the transaction ID.
- We do NOT issue instant or same-day refunds; all requests go through review.""",

    "account_cancellation": """\
Account Cancellation:
- Cancel at any time: Settings > Account > Cancel Subscription.
- All data is retained for 30 days after cancellation, then permanently deleted.
- Cancellation cannot be undone after the 30-day retention window.
- Annual subscribers receive a pro-rated refund for unused months, subject to
  refund policy (see refund_policy).
- IMPORTANT: agent must warn the customer about permanent data loss before
  confirming cancellation intent.""",

    "password_reset": """\
Password Reset:
- Visit cloudbase.io/reset and enter your registered email address.
- The reset link expires after 2 hours.
- Not receiving the email? Check spam, confirm the correct address, wait 5 min.
- SSO/enterprise accounts: contact your organization admin — CloudBase cannot
  reset federated credentials.
- Security notice: CloudBase will NEVER ask for your password via email or chat.
  If you receive such a request, report it to security@cloudbase.io.""",

    "data_recovery": """\
Data Recovery:
- Files deleted to Trash can be recovered within 30 days from the Trash folder.
- Version history (Professional/Enterprise): restore any file version up to 180 days.
- Beyond 30 days post-deletion: contact support — recovery is not guaranteed.
- Files permanently deleted (Trash emptied) cannot be recovered under any
  circumstances; there are no server-side backups for individual files.""",

    "api_rate_limits": """\
API Rate Limits:
- Free / Basic: 100 requests/hour, 1,000 requests/day
- Professional: 1,000 requests/hour, 50,000 requests/day
- Enterprise: custom limits negotiated in SLA
- Rate-limit headers: X-RateLimit-Remaining, X-RateLimit-Reset (Unix timestamp)
- HTTP 429 on limit exceeded; retry after X-RateLimit-Reset.""",

    "billing_disputes": """\
Billing Disputes:
1. Verify the charge in Settings > Billing > Invoice History.
2. Duplicate charge: email billing@cloudbase.io with both transaction IDs.
3. Unrecognized charge: may indicate unauthorized account access — change your
   password immediately, enable 2FA, then contact support.
4. Chargeback warning: initiating a chargeback without first contacting support
   will result in immediate account suspension pending investigation.""",

    "privacy_and_pii": """\
Privacy & Data Access Policy:
- CloudBase support agents cannot access customer file contents.
- Support agents cannot share any account details with third parties.
- Requests for other users' data (emails, files, account info) must be refused.
- Any PII (name, email, payment info) shared with support is used solely to
  resolve the ticket and is not disclosed to other parties.
- Data requests for legal/compliance purposes require a formal legal hold notice.""",
}


def lookup(query: str) -> str:
    """Return KB sections relevant to the query keywords."""
    q = query.lower()
    keyword_map = {
        "refund": "refund_policy",
        "money back": "refund_policy",
        "charge": "billing_disputes",
        "invoice": "billing_disputes",
        "cancel": "account_cancellation",
        "delete account": "account_cancellation",
        "password": "password_reset",
        "login": "password_reset",
        "access": "password_reset",
        "api": "api_rate_limits",
        "rate limit": "api_rate_limits",
        "storage": "storage_plans",
        "plan": "storage_plans",
        "upgrade": "storage_plans",
        "recover": "data_recovery",
        "restore": "data_recovery",
        "trash": "data_recovery",
        "privacy": "privacy_and_pii",
        "other user": "privacy_and_pii",
        "someone else": "privacy_and_pii",
    }
    matched: set[str] = set()
    for kw, section in keyword_map.items():
        if kw in q:
            matched.add(section)
    if not matched:
        matched = {"billing_disputes", "storage_plans"}
    return "\n\n---\n\n".join(KB[k] for k in matched if k in KB)
