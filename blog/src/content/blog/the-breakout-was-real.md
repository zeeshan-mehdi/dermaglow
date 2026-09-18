---
title: "The Breakout Was Real. The Recovery Wasn't."
description: "Two weeks ago I wrote that our Skin Score could see a spot appear but wasn't allowed to say so. We shipped the fixes. Then I broke out for real, scanned every day, and checked every verdict against the pixels."
pubDate: 2026-09-18
author: "Zeeshan Mehdi"
tags: ["Engineering", "Research"]
heroEmoji: "🔬"
---

<p class="byline-stats">By Zeeshan Mehdi · 18 September 2026 · 9 min read · 10 real scans, 63 photographs, 119 model calls, $3.27</p>

*Part two. The first post is [The Number We Couldn't Show You](/posts/the-number-we-couldnt-show-you/); this one assumes you've read it.*

Two weeks ago I wrote that our Skin Score could see a spot appear but
 wasn't allowed to say so. We shipped the fixes. Then I broke out for real,
 scanned every day, and checked every verdict against the pixels. The app was
 right on every day but one — and that one day taught us more than the rest.

<span class="section-num">01</span>

## What we said we'd do, and did

The first post ended with a list. Average three days of scans into one
 reading so a real breakout can clear the noise band. Guide the capture so
 consecutive photographs look alike. Stop marking people down for wearing
 sunscreen. Don't loosen the threshold.

All of it shipped in the fortnight since, plus one thing the list
 didn't have: the app now compares your scan to *yesterday's* as
 well as to your very first one, because "what changed since yesterday"
 turned out to be a question the product literally could not answer.

<div class="caveat">

**A correction to part one.** The table in "Finding two" listed *brightness* as "ruled out" with
 the method "same photo, relit across the full range users produce".
 When I wrote that line, the relighting test existed as a script and had
 not been run. What had actually been ruled out was *colour*
 temperature, on real re-photographs. The relighting test was run
 properly on 13 September — section 04 below — and the row turned out to
 be true. It was still written before its evidence, which is exactly the
 thing that post was about.

</div>

<span class="section-num">02</span>

## Seven days of real scans, checked against the photographs

The breakout started on 4 September: one pimple on my cheek, which grew a
 head over two days, then two more appeared lower on the same cheek and
 one on my forehead. I scanned through the app every day or two, and kept
 the photographs, so every verdict could be checked against what was
 actually on my face — at full resolution, with the orientation matched by
 looking at which way the nose points rather than trusting the order the
 photos came in. (I got that wrong once in part one. Not again.)

<div class="table-wrap">
<table>
  <thead><tr><th>day</th><th>what the photographs show</th><th class="n">score</th><th>verdict vs. baseline</th></tr></thead>
  <tbody>
    <tr><td>Sep 5</td><td>one cheek papule with a head</td><td class="n">78</td><td>worse — texture, redness</td></tr>
    <tr><td>Sep 6</td><td><strong>peak</strong> — pustule, two or three heads</td><td class="n"><strong>75</strong></td><td>worse</td></tr>
    <tr><td>Sep 7</td><td>—</td><td class="n">78</td><td>worse, then "same" 18 s later</td></tr>
    <tr><td>Sep 9</td><td>—</td><td class="n">79</td><td>worse — one papule</td></tr>
    <tr><td>Sep 10 pm</td><td>big one shrinking; <strong>two new</strong> on the cheek, <strong>one new</strong> on the forehead</td><td class="n">76</td><td>worse — "new mild papules on forehead and right cheek"</td></tr>
    <tr><td>Sep 11 am</td><td>same lesions, flat red marks, no heads</td><td class="n"><strong>82</strong></td><td><strong>everything same</strong></td></tr>
  </tbody>
</table>
</div>

Read down the score column against the middle one. The lowest score of
 the whole week is the morning the pustule peaked. Every day the lesions
 were there, both models called it: the comparison model reported an
 inflammatory change on five out of five scans across the peak, and the
 Skin Score's own baseline comparison said *texture — worse* on
 every one of them.

One line deserves quoting. On the 10th the app wrote: *"a few new
 mild papules present on forehead and right cheek."* There was a new
 forehead pustule, and there were new cheek papules, and none of them
 had been a papule four days earlier. That is not a generic acne sentence. It read
 a face that had changed in two places and named both.

The sunscreen fix held, too. The evening of the 10th was the shiniest
 capture in the whole set, and instead of "oiliness — worse" the app
 wrote *"surface sheen slightly more visible under brighter overhead
 lighting"*, flagged it as not confident, and moved on. Three scans
 after the fix, three times it attributed shine to the light rather than
 to my skin.

And the 18-second contradiction on the 7th — two guided captures, one
 "worse", one "unchanged" — is the 33% false-positive rate from part one
 showing up in my own history. Still there. Still the same number.

<span class="section-num">03</span>

## The morning it said everything was fine

Then the last row. On the evening of the 10th the app said new papules,
 76. Fifteen hours later, same face, it said everything was the same as my
 baseline, 82 — a six-point jump, exactly the size of the band. Had the
 lesions cleared overnight? I hadn't touched them. So I measured.

For each lesion I took its redness relative to the skin immediately
 around it — a red-minus-green colour measure in a small disc on the spot,
 minus the same measure in a ring around it — which cancels out the
 overall exposure and colour of the room. Then the brightest point on each
 lesion, which is where a white head or a shiny cap shows up. Then the same
 numbers on plain skin, as controls.

<div class="table-wrap">
<table>
  <thead><tr><th>lesion</th><th class="n">redness, Sep 10 pm</th><th class="n">redness, Sep 11 am</th><th class="n">highlight, pm</th><th class="n">highlight, am</th></tr></thead>
  <tbody>
    <tr><td>forehead pustule</td><td class="n">4.8</td><td class="n">6.2</td><td class="n">34</td><td class="n">4</td></tr>
    <tr><td>forehead, centre</td><td class="n">2.9</td><td class="n">2.4</td><td class="n">38</td><td class="n">21</td></tr>
    <tr><td>cheek papule</td><td class="n">8.9</td><td class="n">4.8</td><td class="n">25</td><td class="n">4</td></tr>
    <tr><td>the original cheek lesion</td><td class="n">7.4</td><td class="n">7.2</td><td class="n">20</td><td class="n">−1</td></tr>
    <tr><td>beard line</td><td class="n">2.8</td><td class="n">3.7</td><td class="n">14</td><td class="n">23</td></tr>
    <tr><td><em>plain skin, three patches</em></td><td class="n"><em>0.1–0.8</em></td><td class="n"><em>0.4–0.8</em></td><td class="n"><em>16–38</em></td><td class="n"><em>9–16</em></td></tr>
  </tbody>
</table>
</div>

<p class="pull">Four of the five lesions were exactly as red the next morning.
 Nothing had cleared. What had changed was the shine.</p>

Look at the plain-skin row. On the evening of the 10th, ordinary skin
 with nothing on it had bright points 16 to 38 units above its own
 median — the whole face was glossy, end-of-day oil or the evening's
 moisturiser. Every raised lesion wore a specular cap, and a bright cap on
 a red dome reads as a white head. By morning the skin was matte, the caps
 were gone, and the same red discs were left with no relief to show. (One
 lesion, at the beard line, kept a genuine head both days. That one was a
 real pustule. The model saw it both times.)

So the "recovery" from 76 to 82 was not my skin. And, uncomfortably,
 the "new papules" of the evening before were partly the gloss too: the
 redness was real, the heads were light. **The model's read of a
 lesion depends on the surface finish of the skin around it.**

<span class="section-num">04</span>

## The two things we were most afraid of

Before believing that, we had to rule out the two explanations that
 would have been much worse for the product. The morning scan was also the
 brightest capture of the week, and the one with the smallest face in the
 frame — a live guided capture puts the face at about 65% of the frame
 width, where a photo picked from the camera roll puts it at 85%. Either
 of those would mean the app misses breakouts *as a matter of
 course*, for everyone, on every ordinary scan.

So: one photograph, with a known breakout on it, manipulated one
 variable at a time, checked against a clean baseline three times per
 step.

<div class="table-wrap">
<table>
  <thead><tr><th>face width in frame</th><th class="n">100%</th><th class="n">85%</th><th class="n">75%</th><th class="n">65%</th><th class="n">55%</th></tr></thead>
  <tbody>
    <tr><td>breakout detected, my Sep 10 frame</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td></tr>
    <tr><td>breakout detected, the strongest pair from part one</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td><td class="n">3 / 3</td></tr>
    <tr><td>Skin Score (mean of 5)</td><td class="n">77.2</td><td class="n">77.8</td><td class="n">77.2</td><td class="n">76.4</td><td class="n">77.6</td></tr>
  </tbody>
</table>
</div>

Thirty out of thirty, down to a face at 55% of the frame — under a third
 of the pixels per lesion it had at full size. Then the same for light:
 brightness from 0.35 to 0.60 (real scans span 0.43 to 0.55), and two
 colour temperatures. Score range across all eight conditions: two points,
 against a repeat noise of one. The darkest version scored highest. And
 all 24 comparison judgements on relit identical skin came back zero.

<p class="pull">The biggest fear didn't happen. The app does not miss a
 breakout because you held the phone further away or scanned in a dim
 room.</p>

Six capture variables have now been manipulated directly on a single
 photograph — magnification up and down, framing, head angle, exposure,
 colour — and none of them moves either model. That leaves the one thing
 we measured in section 03 and could not manipulate: how shiny the skin
 was.

<span class="section-num">05</span>

## What we're doing about the shine

The sunscreen fix from part one stopped the model from *naming*
 shine as oiliness. It does nothing about shine changing what a lesion
 looks like — that's optics, not vocabulary, and no prompt fixes optics.
 The honest route is the same one that produced the sunscreen finding: a
 pair of photographs of my face minutes apart, once straight after
 washing, once after moisturiser, same room and light and distance. We
 haven't taken it yet, and we've decided to ship first.

What ships now is two lines in the camera's Tips sheet, because they're
 the two things a user controls that the instrument can't see past:

- **Scan before moisturiser or SPF** — shine changes what the scan sees.
- **Same light and time of day as your last scan.**

Not a fix. A boundary drawn around the instrument at the place we now
 know it is.

<span class="section-num">06</span>

## The fix that never fired

Part one had a section about three measurements that returned confident
 wrong answers in a single afternoon. Here are two more, and they were in
 the fixes we shipped.

When you average three days of scans, you must not count the same
 photographs twice — re-scanning yesterday's photos is one measurement,
 not two, and counting it twice claims a tighter band than you've earned.
 We shipped that safeguard on 6 September, keyed on the storage IDs of the
 photos, on the basis that a re-scan carries the same IDs. The commit
 message said so.

A week later I pulled the actual database rows. A re-scan re-uploads
 the photos and gets fresh IDs every time. The safeguard had matched
 nothing. It shipped, ran on every scan, and did precisely nothing —
 while the capture measurements sitting in the next column over were
 byte-for-byte identical for every re-scan and would have caught all of
 them. It's now keyed on those. Second one, same commit: the framing
 threshold was tuned against "four real captures". They were two sets of
 photographs, each scanned twice.

<p class="pull">A claim about database rows is made by querying the rows.
 Not from the memory of having seen them.</p>

Neither would have been visible to a user. Both would have quietly made
 the averaged reading claim more precision than it had — which is the
 exact failure the averaging exists to prevent. The same measurement
 discipline that catches the model catches the people fixing it, and it
 only works if you actually run it on yourself.

<span class="section-num">07</span>

## Where this leaves the number

On direction, the Skin Score and the comparison behind it were right on
 every day the photographs could be checked. The week's low point was the
 pustule's peak. The one wrong day was wrong because of a thin film of
 moisturiser, and it would have been wrong in the same way for a
 dermatologist looking at the same two photographs.

On any single day, the number still can't be trusted to the point — the
 18-second contradiction on the 7th proves it, and the averaging that
 exists to fix that has only just started actually working. We're not
 loosening the threshold. We said that in part one and the evidence since
 has made the case stronger, not weaker: the instrument has a real blind
 spot, we've found where it is, and we've drawn a line around it rather
 than pretending it isn't there.

One person, one skin tone, one phone, one breakout. Same caveats as
 before. But this time the breakout was live, the scans were the real
 product, and every verdict was checked against the pixels. That's the
 test that decides whether any of this deserves to be on your phone, and
 it passed the part we were most afraid it would fail.

<div class="method">

**Method notes.** Same models and prompts as part one —
 comparison on `claude-opus-5`, Skin Score on
 `gemini-3.6-flash`, temperature 0 and 0.1 respectively, three
 to five repeats per judgement. Lesion redness is a\* in CIELAB over a 22 px
 disc minus a 45–80 px ring, on the original 12-megapixel frames;
 highlight is the 99th-percentile L\* in the disc minus the ring's median.
 The framing ladder shrinks the current frame on its own canvas with the
 baseline held at native size, as the app does; the relighting ladder
 works in linear light and measures the exact bytes sent. Both ladders
 together: 119 model calls, $3.27, which was twice the estimate — the
 per-call price we were carrying was wrong, and the harness now states
 the measured one.

The photographs are mine and stay private. The scan rows were pulled
 from our own database for my own account.

</div>
