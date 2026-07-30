---
status: ready
initiative: foia
to: April.Lundberg@cityofchicago.org (cc DOFfoia@cityofchicago.org)
subject: Re: FOIA request — Smart Streets pilot violation data (bike/bus lane camera enforcement)
drafted: 2026-07-29
sent: —
tracking: F146238-072126
tracker: #33
---

# Courtesy notice: the F146238-072126 production includes individual names

**Send as a reply on the existing thread**, so it threads under the original
request and April Lundberg can match it to the file she sent.

**Send from `jaredthomasmeyer@gmail.com`, not the project address.** This one is
the exception to the requester-identity rule in `docs/foia/log.md`: request
F146238-072126 was filed personally, before the rule took effect, and DOF's
response came to that address. A reply from an address the officer has never seen
would read as a stranger asking about someone else's request. Sign as the
project; send from the address on file.

## Why send this at all

DOF withheld license plates and addresses, and released owner names. 82,880 of
the 112,318 rows name a private individual next to the violation they received.
The original request had offered to give exactly those up.

The likeliest explanation is a routine export that was never trimmed for this
request. Telling them costs nothing, takes one paragraph, and is the difference
between a requester who handles a mistake quietly and one who does not. FOIA
officers remember both. This program is one OYL expects to keep asking about.

The tone is deliberately flat. It reports a fact, states what the project did
about it, and asks for nothing. It does **not** argue that DOF erred, offer a
legal reading, or invite a correction — any of which turns a courtesy into a
dispute and a dispute into a slower next request.

---

## The message

Dear Ms. Lundberg,

Thank you for the response to F146238-072126, and for turning it around well
ahead of the extended deadline. The data is exactly what we were hoping to work
with.

One thing I want to flag, as a courtesy rather than a complaint. The released
spreadsheet includes the `Owner First Name` and `Owner Last Name` fields for all
registrants, including private individuals — roughly 82,000 of the 112,318 rows.
Our request had stated that we did not object to the redaction of personal
identifying information for individual registrants, and that we were interested
in business and commercial-fleet names.

We are not publishing the individual names. Our project's public repository
carries only a version of the data with those names removed and replaced by an
individual/business marker, and the file as received is kept privately. I am
raising it only in case your office would want to look at the export before it
goes out to any other requester, since I expect this program will draw more
requests.

Two smaller notes on the same production, neither urgent:

- The data dictionary or field layout requested as item 3 was not included. If
  one exists, it would help us interpret `Fine Level 1` and `Ticket Queue`
  correctly rather than by inference.
- Item 2, the compiled dataset behind the Tribune's July 19 report, was not
  provided separately. If the violation-level file supersedes it, that is a
  complete answer and I do not need anything further.

Finally, I will repeat the offer from the original request. If the Department
would consider publishing Smart Streets violation data on the City's Data Portal
on a recurring basis, as it already does for the Speed Camera and Red-Light
Camera datasets, we would use and publicize it, and it would spare your office
requests like this one.

Thank you again for a prompt and thorough response.

Sincerely,
Jared Meyer
On Your Left! — an open-source Chicago bike-safety data project
jaredthomasmeyer@gmail.com
https://jartinator.github.io/chicago-safe-streets-data/

---

## On send

1. Set `status: sent` and `sent: 2026-__-__` above.
2. Note it on the `docs/foia/log.md` row 4 follow-up column.
3. Check the box on tracker issue #33.

If DOF replies with a data dictionary or the item 2 production, that is a new
release against the same reference — add it to
`data/foia/F146238-072126/records/` and update the manifest.
