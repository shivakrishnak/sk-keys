---
id: SYD-073
title: Email System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001, SYD-011
used_by: ""
related: SYD-001, SYD-011, SYD-013, SYD-057, SYD-054
tags:
  - architecture
  - email
  - messaging
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 73
permalink: /syd/email-system-design/
---

# SYD-073 - Email System Design

⚡ TL;DR - Email systems must handle massive asymmetric
scale (send millions per minute, receive billions in
storage) with strict deliverability requirements.
Key challenges: (1) Deliverability - ISPs reject email
from IPs with bad reputation, requiring SPF/DKIM/DMARC
authentication and warm-up periods for new sending IPs;
(2) Fanout for bulk sends - a single marketing email
to 10 million subscribers requires distributed fanout
(message queue + worker fleet); (3) Inbox at scale -
storing all emails for all users indefinitely requires
tiered storage (recent emails hot, archived emails cold);
(4) Spam filtering - real-time classification of inbound
emails before delivery; (5) Rate limiting - protect
sending reputation by throttling per-user and per-ISP.

| #073 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | System Design - Core, Message Queue Design | |
| **Related:** | Core System Design, Message Queue Design, Rate Limiter Design, Event-Driven Architecture, E-Commerce Platform Design | |

---

### 🔥 The Problem This Solves

A startup sends a "Flash Sale!" email to 10 million
subscribers. Simple approach: iterate through the list
and call an SMTP server 10 million times sequentially.
At 100 emails/second: 100,000 seconds = 27 hours.
The sale is over before half the emails are sent.
The solution: distributed fanout. Write one campaign
record to the database. Enqueue 10 million delivery
jobs to a message queue. 100 worker machines each
process 100,000 jobs at 1,000 emails/second = 100,000
total emails/second. 10 million emails in 100 seconds.

---

### 📘 Textbook Definition

**Email system:** A platform for composing, sending,
routing, storing, and delivering electronic messages
between users. Components: SMTP (outbound), IMAP/POP3
(inbound/retrieval), MX records (DNS routing for inbound).

**MTA (Mail Transfer Agent):** Software that transfers
email between servers using SMTP. Postfix, Sendmail,
Exchange are MTAs. Also the "relay" between your
application and the Internet.

**MX record:** A DNS record that specifies which server
handles inbound email for a domain. Email to
user@example.com: DNS lookup for MX records on example.com.
→ Routes to mail.example.com.

**SPF (Sender Policy Framework):** DNS record listing
authorized IP addresses allowed to send email from
your domain. Prevents spoofing from unauthorized IPs.

**DKIM (DomainKeys Identified Mail):** Cryptographic
signature added to email headers. Receiving server
verifies signature using public key in DNS. Proves
email was sent by (and not modified by) your domain.

**DMARC:** Policy specifying what to do when SPF or
DKIM fails: none (monitor), quarantine (spam folder),
reject (block). Requires both SPF and DKIM.

**Deliverability:** The probability that a sent email
reaches the recipient's inbox (not spam folder or
bounced). Determined by IP reputation, domain reputation,
content quality, bounce rate, and spam complaint rate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Send fast with queue + worker fleet. Receive with
MTA + spam filter. Store tiered. Authenticate with
SPF/DKIM/DMARC to avoid spam folder.

**One analogy:**
> The postal system:
>
> Sending: Your company has a mail room (SMTP service).
> For a mass mailing (marketing email): print 10M letters
> simultaneously across 100 printers, sorted by region,
> sent to each region's post office (ISP gateway).
>
> Receiving: Your address (MX record) tells the postal
> system which post office to bring mail to.
> Mail arrives at the post office (MTA).
> Mail clerk checks for junk (spam filter).
> Legitimate mail goes to your mailbox (inbox).
>
> Authentication: Your mail has a certified seal
> (DKIM signature). Forged mail without the seal
> goes to junk.

**One insight:**
Email deliverability is the most underestimated
challenge. A technically correct email can go to
spam 100% of the time if: (1) it's sent from a new
IP with no sending history; (2) it has a high bounce
rate (sending to invalid addresses); (3) recipients
mark it as spam; (4) SPF/DKIM/DMARC is misconfigured.
Warming up a new sending IP requires sending a gradually
increasing volume over weeks (start 1,000/day, double
weekly). Gmail/Yahoo rate-limit new senders. Ignoring
deliverability means your emails disappear silently.

---

### 🔩 First Principles Explanation

**OUTBOUND EMAIL PIPELINE (transactional):**
```
Application (order confirmation email):

1. App service calls Email API:
   POST /api/emails
   {to: user@gmail.com, subject: "Order #123",
    template: "order_confirmation",
    data: {order_id: 123, ...}}

2. Email API service:
   - Validate recipient address format
   - Check if recipient has unsubscribed
   - Check sending limits for this user/template
   - Write email job to queue (SQS/Kafka)
   - Return {message_id: "msg_abc123"}

3. Queue workers (sending fleet):
   - Pick up job from queue
   - Render template with data
   - Call SMTP relay (SES, SendGrid, Postfix)
   - SMTP relay → destination MTA (Gmail, Outlook)

4. Delivery tracking (webhooks from SMTP relay):
   - delivered: email accepted by recipient MTA
   - opened: tracking pixel loaded (optional)
   - clicked: link tracking (optional)
   - bounced: recipient address invalid
   - complained: recipient marked as spam

5. On bounce: mark email address as invalid in DB.
   Future sends to this address: skip (save reputation).
   On complaint: unsubscribe user immediately.
```

**BULK EMAIL FANOUT (marketing):**
```
Campaign: 10 million subscribers.

WRONG (naive):
  for user_id in all_subscribers:
    send_email(user_id)  # 10M iterations, serial

RIGHT (distributed fanout):

1. Campaign API: INSERT campaign record (DB).
2. Campaign API: publish one event to Kafka:
   {campaign_id: 456, segment: "all_subscribers"}

3. Fanout service: consumes the event.
   Queries subscriber list in batches (1,000/batch).
   Publishes 10,000 batch jobs to email_delivery queue.
   Each batch: [user_id_1..1000], template, campaign_id.

4. Worker fleet (100 machines × 100 goroutines):
   Each worker: picks 1 batch job.
   Renders 1,000 emails from template (personalization).
   Calls SMTP relay in parallel (100 concurrent calls).
   Rate limit: 1,000 emails/second per worker.
   Total: 100 workers × 1,000/s = 100,000 emails/sec.
   10M emails: 100 seconds.

Rate limiting per ISP:
  Gmail: 50 connections maximum from one IP.
  Send workers must respect per-ISP connection limits.
  Otherwise: Gmail blocks the IP.
  Use dedicated sending pools per ISP.
  
IP warming (for new campaigns on new IPs):
  Week 1: 1,000 per day per IP.
  Week 2: 5,000 per day.
  Week 3: 20,000 per day.
  Gradually build sending reputation before scaling.
```

**INBOX STORAGE (receiving email):**
```
Users: 100M. Average inbox: 10,000 emails. 
Average email: 20KB. Total: 100M × 10K × 20KB = 20PB.

Tiered storage:
  Hot (Redis + SSD):
    Recent 30 days. Fast search. Small footprint.
    Read pattern: constant (inbox view, search).
    
  Warm (S3 Standard):
    31 days - 1 year. Occasional access.
    Lifecycle policy: move from hot after 30 days.
    
  Cold (S3 Glacier):
    > 1 year. Archive. Rare access.
    Retrieved on explicit request (takes minutes).
    Cost: $0.004/GB/month vs $0.023 for Standard.

Email body storage:
  Headers/metadata: PostgreSQL (fast search, filter).
  Body content: S3 (keyed by email_id).
  Attachments: S3 (with lifecycle policies).
  
Indexing for search:
  Full-text search: Elasticsearch or PostgreSQL FTS.
  Index: sender, recipient, subject, body, date.
  At 100M users × 10K emails: ~1 trillion records.
  Shard by user_id. Each shard handles ~100K users.
```

**AUTHENTICATION (SPF/DKIM/DMARC):**
```
DNS records for example.com:

SPF:
  TXT "v=spf1 ip4:192.168.1.0/24 
       include:amazonses.com ~all"
  Allows: your IPs + SES.
  ~all: soft fail (quarantine) if not in list.
  -all: hard fail (reject) if not in list.

DKIM:
  Selector: TXT mail._domainkey.example.com
  "v=DKIM1; k=rsa; p=MIGfMA0GCSq..."  (public key)
  
  Sending server signs email with private key.
  Receiving server fetches public key from DNS.
  Verifies signature. Pass = legitimate sender.

DMARC:
  TXT _dmarc.example.com
  "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"
  
  p=none: monitor only (don't block).
  p=quarantine: failed emails → spam folder.
  p=reject: failed emails → blocked entirely.
  
  Start with p=none, monitor reports,
  fix issues, gradually move to p=reject.
```

---

### 🧪 Thought Experiment

**Email vs. Push Notification for Alerts**

Design choice: notify users of events.

Email:
- Delivery: guaranteed (retries, bounce handling).
- Latency: seconds to minutes.
- Storage: recipient's inbox (history).
- Best for: receipts, weekly digests, legal notifications.

Push notification (mobile):
- Delivery: best-effort (device must be online).
- Latency: sub-second to seconds.
- Storage: none (transient).
- Best for: real-time alerts (payment received,
  new message, sports score).

SMS:
- Delivery: high (carrier network, not internet).
- Latency: seconds.
- Cost: $0.01-0.05 per message.
- Best for: 2FA, critical alerts, no smartphone.

Multi-channel:
For critical notifications (bank transaction):
Send all three. Ensure at-least-one delivery.
User receives first one that arrives; rest are
de-duplicated (user saw the notification already).

---

### 🧠 Mental Model / Analogy

> Email architecture is like a multi-tier courier service:
>
> Transactional email (receipts): express courier.
> One package, one recipient. Priority delivery.
>
> Marketing email: freight shipping company.
> One manifest (campaign), 10M packages. Routed to
> regional distribution centers (ISP gateways) and
> delivered by local couriers (ISP mail servers).
>
> Authentication: customs declaration + certified seal.
> Without it: customs holds or rejects the shipment.
>
> Deliverability: your company's shipping reputation.
> Too many returns (bounces) or complaints:
> customs blocks your future shipments.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An email system sends and receives electronic messages.
The hard part: making sure millions of emails actually
arrive in people's inboxes (not spam), storing them
efficiently, and handling replies and attachments.

**Level 2 - How to use it (junior developer):**
Use an email service (SES, SendGrid, Mailgun) - don't
run your own SMTP server. Verify your domain (SPF,
DKIM). Send transactional emails via API (not SMTP from
your app directly). Handle bounces and complaints via
webhooks - unsubscribe bounced addresses immediately.
Use a queue for bulk sending. Never send from your
app server's IP directly.

**Level 3 - How it works (mid-level engineer):**
Transactional: API → queue → worker → SMTP relay → MTA.
Bulk: campaign → fanout service → delivery queue →
worker fleet → SMTP relay with per-ISP rate limiting.
Authentication: SPF (IP whitelist), DKIM (signature),
DMARC (policy). Bounce handling: hard bounce (invalid
address) → mark invalid forever; soft bounce (mailbox
full) → retry with backoff. Storage: tiered (hot/warm/cold).

**Level 4 - Why it was designed this way (senior/staff):**
Email is the oldest federated internet protocol (RFC 5321,
SMTP from 1982). The lack of a central authority means
deliverability is governed by reputation, not just
correctness. ISPs developed spam filters and reputation
systems to defend against the massive spam problem of
the early 2000s. SPF (2003), DKIM (2004), DMARC (2012)
emerged as industry standards to restore trust in email
authentication. The distributed nature of email means
there is no single "delivery confirmed" signal: SMTP
reports acceptance at the next hop, not final delivery
to the inbox. Gmail/Yahoo feedback loops (FBL) report
spam complaints back to senders, but only for large
senders with established relationships.

**Level 5 - Mastery (distinguished engineer):**
Gmail's Postmaster Tools API (2015) revealed how Google
scores domain and IP reputation. Key signals: (1) spam
rate: if > 0.1% of your emails are marked spam by Gmail
users, you're on a watch list; if > 0.3%, hard restrictions
apply; (2) IP reputation: shared IPs carry others' bad
reputation; dedicated IPs require warming; (3) domain
reputation: distinct from IP - a domain can be transferred
to new IPs. Yahoo's 2024 announcement requiring DMARC
enforcement for bulk senders (> 5,000/day) forced the
entire industry to implement DMARC within months. Apple
iCloud Mail's Sender Policy changed inbox placement
algorithms to heavily weight DKIM alignment (from=
header must match DKIM d= tag). These ecosystem-wide
changes illustrate that email deliverability is a moving
target requiring continuous monitoring via Postmaster
Tools and DMARC aggregate reports.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ EMAIL SEND FLOW                                     │
│                                                      │
│ App → POST /emails → Email API                    │
│   → Validate, check unsubscribes, rate limits    │
│   → Enqueue (SQS/Kafka)                          │
│                                                      │
│ Worker fleet:                                       │
│   Dequeue → render template                      │
│   → SMTP relay (SES/SendGrid)                    │
│     → DNS MX lookup for recipient domain         │
│     → SMTP connect to recipient MTA             │
│     → SMTP DATA (email + DKIM signature)        │
│     → MTA accepts (250 OK) or rejects (5xx)    │
│                                                      │
│ Webhook (delivery events):                          │
│   delivered / bounced / complained               │
│   → Update email status in DB                   │
│   → Bounced: mark address invalid               │
│   → Complained: unsubscribe immediately          │
│                                                      │
│ DNS records:                                        │
│   SPF: "v=spf1 include:amazonses.com ~all"       │
│   DKIM: mail._domainkey → public key             │
│   DMARC: _dmarc → p=reject                      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Email service with queue (Python)**
```python
import boto3
import json
import uuid
from datetime import datetime

sqs = boto3.client('sqs')
ses = boto3.client('ses', region_name='us-east-1')

EMAIL_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/..."
UNSUBSCRIBE_CHECK_CACHE = {}  # Redis in production

class EmailService:
    def send_transactional(
            self,
            to_email: str,
            template_id: str,
            template_data: dict,
            priority: str = "normal") -> str:
        """Queue a transactional email for delivery."""
        
        # 1. Check unsubscribe list
        if self._is_unsubscribed(to_email):
            return None  # Skip silently
        
        # 2. Validate email format
        if not self._is_valid_email(to_email):
            raise ValueError(f"Invalid email: {to_email}")
        
        # 3. Check if address is hard-bounced
        if self._is_hard_bounced(to_email):
            return None  # Skip: address is invalid
        
        # 4. Enqueue for async delivery
        message_id = str(uuid.uuid4())
        job = {
            "message_id": message_id,
            "to": to_email,
            "template_id": template_id,
            "template_data": template_data,
            "priority": priority,
            "queued_at": datetime.utcnow().isoformat()
        }
        
        sqs.send_message(
            QueueUrl=EMAIL_QUEUE_URL,
            MessageBody=json.dumps(job),
            MessageGroupId=to_email,  # FIFO queue grouping
            MessageDeduplicationId=message_id
        )
        return message_id

    def process_email_job(self, job: dict):
        """Worker: process one email delivery job."""
        # Render template
        html = self._render_template(
            job['template_id'], job['template_data'])
        text = self._render_template_text(
            job['template_id'], job['template_data'])
        
        # Send via SES
        try:
            response = ses.send_email(
                Source="noreply@example.com",
                Destination={"ToAddresses": [job['to']]},
                Message={
                    "Subject": {"Data": self._get_subject(
                        job['template_id'],
                        job['template_data'])},
                    "Body": {
                        "Html": {"Data": html},
                        "Text": {"Data": text}
                    }
                },
                # Idempotency: SES uses this to prevent
                # duplicate sends for same message_id
                # on retries
                ConfigurationSetName="MyConfigSet"
            )
            
            # Track delivery attempt
            db.execute(
                "INSERT INTO email_logs "
                "(message_id, to_email, status, "
                " ses_message_id) "
                "VALUES (%s, %s, 'sent', %s)",
                [job['message_id'], job['to'],
                 response['MessageId']]
            )
            
        except ses.exceptions.MessageRejected as e:
            # Hard failure: mark address
            self._handle_hard_failure(job['to'], str(e))

    def handle_bounce_webhook(self, event: dict):
        """Handle SES bounce/complaint webhooks."""
        notification_type = event.get('notificationType')
        
        if notification_type == 'Bounce':
            bounce = event['bounce']
            if bounce['bounceType'] == 'Permanent':
                # Hard bounce: address is invalid forever
                for recipient in bounce['bouncedRecipients']:
                    self._mark_hard_bounce(
                        recipient['emailAddress'])
            
        elif notification_type == 'Complaint':
            # User marked as spam: unsubscribe immediately
            for recipient in \
                    event['complaint']['complainedRecipients']:
                self._unsubscribe(recipient['emailAddress'])
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
```

**Example 2 - Bulk email fanout**
```python
def send_campaign(campaign_id: int, segment: str):
    """
    Fanout: queue 1 job per 1000 subscribers.
    Do not iterate all subscribers synchronously.
    """
    # Get total subscriber count for progress tracking
    total = db.query_one(
        "SELECT COUNT(*) as n FROM subscribers "
        "WHERE segment = %s AND unsubscribed = false",
        [segment]
    )['n']
    
    batch_size = 1000
    offset = 0
    batch_num = 0
    
    while offset < total:
        # Don't load all IDs into memory at once
        batch_ids = db.query(
            "SELECT id, email FROM subscribers "
            "WHERE segment = %s "
            "AND unsubscribed = false "
            "ORDER BY id "
            "LIMIT %s OFFSET %s",
            [segment, batch_size, offset]
        )
        
        if not batch_ids:
            break
        
        # Enqueue batch as one SQS message
        sqs.send_message(
            QueueUrl=EMAIL_BATCH_QUEUE_URL,
            MessageBody=json.dumps({
                "campaign_id": campaign_id,
                "batch_num": batch_num,
                "recipients": [
                    {"id": r['id'], "email": r['email']}
                    for r in batch_ids
                ]
            })
        )
        
        offset += batch_size
        batch_num += 1
    
    # Update campaign status
    db.execute(
        "UPDATE campaigns SET status='queued', "
        "total_recipients=%s WHERE id=%s",
        [total, campaign_id]
    )
    
    print(f"Campaign {campaign_id}: "
          f"queued {batch_num} batches "
          f"for {total} recipients")
```

---

### ⚖️ Comparison Table

| Email Type | Latency | Volume | Priority | Delivery |
|---|---|---|---|---|
| **Transactional** (receipts, alerts) | < 5 seconds | Low (1 per user event) | High | Required |
| **Triggered** (onboarding, re-engagement) | Minutes | Medium | Normal | Important |
| **Bulk/Marketing** | Minutes-hours | Very high (millions) | Low | Best-effort |
| **System alerts** (monitoring, errors) | < 1 second | Low | Critical | Required |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SMTP from your app server is fine | Sending directly from your application server's IP means your IP has no sending reputation with ISPs. Gmail, Yahoo, and Outlook will route almost all your emails to spam. Additionally, your application server may be on a shared IP range flagged as potentially malicious. Always use a dedicated email sending service (SES, SendGrid, Mailgun) with proper IP warming and reputation management. |
| Email delivery is synchronous | SMTP's "250 OK" response only means the receiving MTA accepted the message. It does not mean the email was delivered to the inbox. The receiving MTA may hold it for spam filtering, defer it due to load, or silently drop it. Track delivery events via bounce webhooks and feedback loops (Google Postmaster, Yahoo FBL). An email is only "delivered" when the recipient's inbox receives it. |
| Unsubscribes are optional for marketing email | The CAN-SPAM Act (US), GDPR (EU), and CASL (Canada) all legally require an unsubscribe mechanism for marketing emails. Ignoring unsubscribe requests can result in FTC fines (up to $51,744 per email), GDPR fines (4% of global revenue), and ISP blocks. More practically: users who can't unsubscribe mark emails as spam instead, devastating your deliverability. Process unsubscribes within 10 business days (CAN-SPAM) or immediately (GDPR best practice). |

---

### 🚨 Failure Modes & Diagnosis

**IP Block: All Emails Going to Spam**

**Symptom:**
Transactional emails (receipts, password resets)
stop reaching users. Support: "I never got the email."
Sending 10,000 emails; 0 opens. Delivery rate: 5%.
No change in code deployed.

**Root Cause:**
A misconfigured bulk send (high bounce rate or spam
complaints) damaged the sending IP's reputation.
Google/Yahoo now route all emails from this IP to spam.

**Diagnosis:**
```bash
# Check IP reputation on major blocklists:
# https://mxtoolbox.com/blacklists.aspx
# Check: MXToolbox → Blacklist check → your sending IP

# Check Google Postmaster Tools:
# https://postmaster.google.com/
# Look for: IP reputation, domain reputation,
# spam rate, delivery errors

# Check bounce rate in SES console or SendGrid:
# Bounce rate > 5%: danger zone
# Bounce rate > 10%: SES suspends account

# DKIM verification:
dig TXT mail._domainkey.example.com
# Should return your public key record
# Use: https://www.mail-tester.com/ - send a test email
# Score < 8/10: configuration issues to fix
```

**Fix:**
```
Short-term:
1. Identify the source of bounces/complaints.
   Was a marketing email sent to an unclean list?
2. Scrub the list (remove invalid addresses).
3. Move to new IP(s): warm them up gradually.
4. Use separate IP pools for transactional vs. marketing.
   Marketing bad reputation should NOT affect
   transactional delivery.

Long-term:
1. Enable SPF, DKIM, DMARC (p=reject).
2. Set up Google Postmaster and Yahoo FBL monitoring.
3. Set bounce threshold alerts:
   - > 2% bounce: pause campaign.
   - > 0.1% spam rate: investigate immediately.
4. Use double opt-in for marketing lists.
   Only send to users who confirmed email address.
   Eliminates invalid addresses from the start.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design - Core` - reliability patterns,
  retry logic, queue-based decoupling
- `Message Queue Design` - email bulk fanout relies
  heavily on message queues (SQS/Kafka)

**Builds On This (learn these next):**
- `Rate Limiter Design` - per-IP, per-domain sending
  rate limits to protect reputation
- `Event-Driven Architecture` - email sending as an
  event-driven system (order placed → email event)
- `E-Commerce Platform Design` - email is a core
  notification channel in e-commerce workflows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SEND PATH   │ App → Queue → Worker → SMTP relay → MTA  │
│             │ Never send direct from app server IP.    │
├─────────────┼──────────────────────────────────────────  │
│ BULK FANOUT │ Campaign → fanout → batch jobs (1K each) │
│             │ Worker fleet: 100K emails/sec.           │
├─────────────┼──────────────────────────────────────────  │
│ AUTH        │ SPF: IP whitelist. DKIM: signature.      │
│             │ DMARC: reject on failure. All 3 required.│
├─────────────┼──────────────────────────────────────────  │
│ BOUNCES     │ Hard bounce (5xx): mark invalid forever. │
│             │ Complaint: unsubscribe immediately.      │
├─────────────┼──────────────────────────────────────────  │
│ REPUTATION  │ Bounce < 2%. Spam rate < 0.1%.          │
│             │ Warm new IPs gradually.                  │
├─────────────┼──────────────────────────────────────────  │
│ STORAGE     │ Tiered: hot (30d) → warm (1yr) → cold.  │
│             │ Metadata: SQL. Body/attachments: S3.    │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Queue + workers + SPF/DKIM/DMARC.     │
│             │  Handle bounces. Separate pools."      │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Game Leaderboard Design                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Bulk email requires distributed fanout: one campaign
   record → queue of batch jobs (1,000/batch) → worker
   fleet processes in parallel. Sequential processing
   is prohibitively slow for millions of emails.
2. SPF + DKIM + DMARC are non-negotiable. Without them:
   emails go to spam or are rejected. Start with
   DMARC p=none (monitoring), fix issues, then move to
   p=reject. Gmail/Yahoo require DMARC enforcement for
   bulk senders (> 5,000 per day) since 2024.
3. Handle bounces and complaints immediately in webhooks.
   Hard bounce → mark address invalid, never send again.
   Spam complaint → unsubscribe immediately.
   Bounce rate > 5% or spam rate > 0.1%: ISPs block
   your sending IP, killing all email delivery.

**Interview one-liner:**
"Email system: transactional (App → SQS → worker → SES/SendGrid) vs. bulk campaign
(campaign → fanout service → batch queue → worker fleet, 100K/s throughput).
Authentication: SPF (IP whitelist) + DKIM (signing) + DMARC (reject policy) -
all 3 required for inbox delivery, not spam. Deliverability: monitor bounce rate
(< 2%) and spam complaint rate (< 0.1%) via Postmaster Tools. Hard bounce → mark
invalid forever. Spam complaint → immediate unsubscribe. Separate IP pools for
transactional vs. marketing email. Storage: SQL metadata + S3 bodies + tiered
archival (hot/warm/cold Glacier)."
