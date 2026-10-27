---
title: "We Grade Our Own Homework"
description: "Before a change to Dermaglow reaches your face, it now has to sit an exam: 33 photographs, 34 coach conversations, the same questions every time. What the first exams found, what we fixed, what we got wrong fixing it, and how your photos stay out of all of it."
pubDate: 2026-10-27
author: "Zeeshan Mehdi"
tags: ["Engineering", "Testing", "Privacy"]
heroEmoji: "📝"
---

<p class="byline-stats">By Zeeshan Mehdi · 27 October 2026 · 18 min read · 8 experiments, 33 photographs, 34 conversations</p>

<figure>
<svg viewBox="0 0 760 250" role="img"
aria-label="Share of skin problems the scan found on the 16 test photos: 72 percent before the fix, 94 percent after. False alarms on healthy skin: none before, none after.">
<text x="0" y="14" class="svg-title">Skin problems the scan found on our 16 test photos</text>
<text x="0" y="62" class="svg-label">before</text>
<rect x="90" y="44" width="630" height="28" fill="var(--band)" rx="3"/>
<rect x="90" y="44" width="454" height="28" fill="var(--ink-3)" rx="3"/>
<text x="552" y="63" class="svg-strong">72%</text>
<text x="0" y="112" class="svg-label">after</text>
<rect x="90" y="94" width="630" height="28" fill="var(--band)" rx="3"/>
<rect x="90" y="94" width="592" height="28" fill="var(--signal)" rx="3"/>
<text x="690" y="113" class="svg-strong">94%</text>
<line x1="90" y1="150" x2="720" y2="150" stroke="var(--rule-2)" stroke-width="1"/>
<text x="0" y="186" class="svg-title">Healthy faces the scan wrongly found a problem on</text>
<text x="0" y="216" class="svg-label">before</text>
<text x="90" y="216" class="svg-strong">0 of 7</text>
<text x="300" y="216" class="svg-label">after</text>
<text x="370" y="216" class="svg-strong">0 of 7</text>
</svg>
<figcaption><strong>The result, up front.</strong> The scan now reports
94% of the skin problems on our test photos, up from 72%, and still finds
no problem on any of the seven healthy faces. The second number is the
one that was hard to keep. Getting the first one up without it was most of
the work.</figcaption>
</figure>

<span class="section-num">01</span>

## Every change is a gamble unless you can measure it

Dermaglow reads your skin from a photograph and talks to you about it. Both of those are done by AI models, and both are steered by instructions we write. Change a sentence in those instructions and the app can start noticing something it used to miss. It can also start seeing redness on a fair face that has none, or call the natural darker skin around someone's mouth a "patch". Often a single change does both at once.

Until this month we judged changes the way most small teams do: try it on a few photos, read the answers, decide it looks better. That works until the day it doesn't, and you find out from a user.

<p class="pull">So we built an exam. Every change now sits it, and the results have to be at least as good as last time.</p>

This post covers the exam itself, the first eight experiments we ran on it, the numbers that came back (including the bad ones), and how all of it is kept away from your photos.

<span class="section-num">02</span>

## The test photographs

An exam is only as good as its questions. We needed photographs of real faces showing the things people actually ask us about: acne, dark marks, redness, oily T-zones, dryness, tired eyes, faint problems that are easy to miss. We also needed plenty of healthy skin, freckles and other things that are *not* problems, because a skin app that finds a problem on every face is useless.

We collected **33 photographs**, every one either openly licensed or ours:

<div class="table-wrap">
<table>
<thead><tr><th>Where from</th><th class="n">Photos</th><th>Why</th></tr></thead>
<tbody>
<tr><td>Wikimedia Commons</td><td class="n">15</td><td>Openly licensed faces: acne, dark spots, freckles, clear skin of many tones</td></tr>
<tr><td>Open-access medical papers (CC BY)</td><td class="n">9</td><td>What's hard to find elsewhere: T-zone shine, redness, mixed red and brown marks, faint problems, a very dry face, tired eyes</td></tr>
<tr><td>Openverse (Creative Commons)</td><td class="n">4</td><td>Everyday clear faces</td></tr>
<tr><td>Our own marketing images</td><td class="n">2</td><td>Images we own the rights to</td></tr>
<tr><td>My own face</td><td class="n">3</td><td>Real photos taken in our app</td></tr>
</tbody>
</table>
</div>

Skin tone matters more here than anywhere. Redness, for example, looks pink on light skin and brown or purple on dark skin, and a model trained mostly on light skin can miss it entirely. The set spans the full Fitzpatrick scale, the standard way dermatologists describe skin from very light (type I) to very dark (type VI): **9 photos of types I–II, 18 of III–IV and 6 of V–VI**. Darker skin is still the smallest group, and adding more is first on our list for the next version.

I deliberately *reduced* the number of my own photos. Early drafts had more of them, but an exam built around one person's face quietly teaches you to build an app for that face.

Each photo was labelled by hand: its skin type, what is on the skin, how it is lit, which way the face is turned. Then every label was reviewed and approved before a single test ran. These labels are our reading of the photos, not a dermatologist's diagnosis. Section 11 comes back to what that means.

<span class="section-num">03</span>

## Five questions, asked the same way every time

We split the exam into small papers, each answering one question, so that when something gets worse we know *what* got worse:

<div class="table-wrap">
<table>
<thead><tr><th>Paper</th><th>The question it answers</th></tr></thead>
<tbody>
<tr><td>Clear skin<br><span class="mono" style="font-size:12px">7 photos</span></td><td>Does it leave healthy skin, freckles and shine alone, and score clear skin the same whatever its colour?</td></tr>
<tr><td>Skin problems<br><span class="mono" style="font-size:12px">16 photos</span></td><td>Does it find what is actually there, without inventing anything?</td></tr>
<tr><td>Same photo, three times<br><span class="mono" style="font-size:12px">4 photos</span></td><td>Does the same photo get the same score every time?</td></tr>
<tr><td>Spot map<br><span class="mono" style="font-size:12px">9 photos</span></td><td>Does the map of your face pin marks and spots in the right places, leave freckles alone, and notice when light comes from the side?</td></tr>
<tr><td>Coach<br><span class="mono" style="font-size:12px">34 messages</span></td><td>When you ask the coach to do something, does it do it, and is it honest about what it did?</td></tr>
</tbody>
</table>
</div>

The papers are locked. The photos, the labels and the questions cannot change without starting a new version of the exam, so a result from today can be compared with a result from next month. If we could quietly swap a hard photo for an easy one, the exam would only ever tell us what we wanted to hear.

Some checks are simple rules. Did the scan use the word "melanoma"? Did it suggest lightening someone's skin? Did it put a "see a doctor" warning on a photo with nothing worrying in it? A computer can check those exactly. Four of them are **safety checks**, and the rule for those is strict: **no change may make a safety check worse, by even one photo**.

<span class="section-num">04</span>

## Where we started: safe, but missing a quarter of what was there

The first exam was the app exactly as it was, so we would have something to measure every later change against. It was good news and bad news.

The good news: every safety check passed. No false "see a doctor". No diagnosis words, no skin-lightening advice. Healthy faces got no invented problems. Clear skin scored within 1.5 points (out of 100) across skin tones. The same photo scored within a point of itself over three runs.

The bad news: on the skin-problem photos it found only **72% of what was there**. What it missed had a pattern:

- **Fine lines**, missed on all three photos that had them.
- **Mixed colours.** On a face with both red and brown marks, it saw the red, filed it as "acne", and never mentioned the background redness on its own.
- **Faint melasma**, the soft brown patches on the cheeks, in dim light.
- **Shine** on a very oily forehead, missed both times we tried.
- **Pores** on a close-up of a cheek.

Not one of these is dangerous to miss. But each is something a person can see in the mirror, and an app that can't see what you can see is an app you stop trusting.

<span class="section-num">05</span>

## Fixing it took three tries. The first two would have hurt people with darker skin.

The fix itself sounds simple: tell the model to list everything it sees, each kind of sign as its own finding, faint ones included. Here is what happened when we ran the exam on it.

### Try one: it found everything, including things that weren't there

The skin-problem paper went from 72% to **100%**. If that were the only paper, we would have shipped it.

The clear-skin paper failed. Healthy faces started getting problems. A fair-skinned face's natural pinkness was reported as redness. On the clear, healthy face with the darkest skin in the set, the natural darker skin around the chin was reported as "a faint patch". That face's score dropped from 90 to 85, and the gap between how the app scored light and dark healthy skin widened from 1 point to 5.

<p class="pull">Told to look harder, the model found "problems" exactly where darker skin is naturally darker.</p>

This is the failure we built the exam to catch, and it caught it on the first try. Without the clear-skin paper, the headline number would have gone up and a fairness problem would have gone out to everyone.

### Try two: better, but not there

We added rules: a faint sign only counts if it differs from the person's *own* surrounding skin; lines only count on adult faces at rest; don't go hunting on a face that is healthy. The fair face was fixed. The chin on darker skin still got its "patch". And the acne photo's score now swung 64, 71, 65 across three identical runs, as borderline pores came and went.

### Try three: all five papers pass

Three more rules did it. Natural darker skin around the eyes, mouth, chin and jaw is never hyperpigmentation. A mild or faint sign moves the score by a point or two at most, so it can't swing a score on its own. And flakes on greasy skin are not dryness.

<div class="table-wrap">
<table>
<thead><tr><th></th><th class="n">Before</th><th class="n">After</th></tr></thead>
<tbody>
<tr><td>Skin problems found</td><td class="n">72%</td><td class="n"><strong>94%</strong></td></tr>
<tr><td>Healthy faces given an invented problem</td><td class="n">0 of 7</td><td class="n">0 of 7</td></tr>
<tr><td>Gap between skin tones on healthy skin</td><td class="n">1.5 points</td><td class="n">1–2 points</td></tr>
<tr><td>Same photo, how far the score moves</td><td class="n">under 1 point</td><td class="n">about 1 point</td></tr>
<tr><td>Safety checks</td><td class="n">all pass</td><td class="n">all pass</td></tr>
</tbody>
</table>
</div>

The one thing still missed is faint melasma in dim light. We'd rather leave that honestly missed than tune the instructions until a single photo passes.

Then we raised the bar. The new results became the standard every future change is measured against, so a later change that slides back towards the old numbers now fails.

<span class="section-num">06</span>

## A second reader for the things rules can't check

Some of what matters most can't be checked with a word list. Did the scan describe colour correctly for this person's skin tone? Did it treat the depth of someone's skin as a problem? Did it sound alarming, or promise results?

For those we added a reviewer: a second AI that reads each written result, never the photograph, together with the person's skin type, and answers four questions true or false, as a dermatologist experienced with every skin tone would.

On the parts that matter most it was spotless: **not once** did the scan treat someone's skin colour as a problem or suggest lightening it.

It also found a real weakness we hadn't seen. **On very dark skin, the scan sometimes wrote "no obvious redness" and took that to mean the skin was calm.** But on dark skin, inflammation often isn't red. It shows as brown, purple or a deeper shade of the person's own colour. Not seeing red is not the same as not seeing inflammation. Our instructions already said so; the model didn't always follow them. That fix is next.

<div class="caveat">

**The reviewer was wrong too, at first.** Its first version marked "pink redness" on medium skin (types III–IV) as a mistake, as if pink could only be described on light skin. That was the reviewer's error, not the scan's: pink redness on a type III face *is* pink. We corrected the reviewer's instructions and re-graded the same answers. An AI grading an AI needs grading too, so we treat its numbers as a pointer to where to look, never as a verdict on its own.

</div>

<span class="section-num">07</span>

## Two ideas that didn't earn their place

Not every experiment produces a change. Two of ours ended in "no", which is still worth knowing.

**Zoomed-in close-ups.** Alongside your full photo, the scan also looks at close crops of your nose and cheeks, at full resolution. It costs extra. We ran the exam with them switched off: it found 76% of problems instead of 72%. That's a single photo's difference, well within the noise between two runs. Our test photos are also far smaller than a real scan from your phone, which is exactly where close-ups should help most. So: not proven either way, and they stay until we can test on full-size scans.

**Telling the AI your skin type.** Would the scan do better on darker skin if we told it the skin type up front? Not a single photo's result changed. Not needed, and one less piece of information about you sent anywhere.

<span class="section-num">08</span>

## Shopping for a different model

New AI models come out every few weeks, and each claims to be better or cheaper. The exam lets us check rather than believe. We ran the same two papers on our current model and two alternatives:

<div class="table-wrap">
<table>
<thead><tr><th></th><th class="n">Our model</th><th class="n">Cheaper sibling</th><th class="n">Fast rival</th></tr></thead>
<tbody>
<tr><td>Skin problems found</td><td class="n">94%</td><td class="n">89%</td><td class="n">97%</td></tr>
<tr><td>False alarms, safety checks</td><td class="n">none</td><td class="n">none</td><td class="n">none</td></tr>
<tr><td>Gap between skin tones (points)</td><td class="n">2</td><td class="n">1</td><td class="n">2.5</td></tr>
<tr><td>Described colour right for the skin tone</td><td class="n">94%</td><td class="n">100%</td><td class="n">69%</td></tr>
<tr><td>Calm, honest about what a photo can't show</td><td class="n">100%</td><td class="n">100%</td><td class="n">0%</td></tr>
<tr><td>Cost</td><td class="n">1×</td><td class="n">about ½×</td><td class="n">about ¾×</td></tr>
</tbody>
</table>
</div>

The fast rival found the most problems, and on a leaderboard it would win. Read its answers and it's the one we'd least want talking to you: it told people their skin was in "excellent overall health" and never once said that a photo has limits. **Finding more is not the same as being more useful.**

The cheaper sibling is the interesting one: half the price, slightly less thorough, and better-worded on colour. It also declined to analyse one photo that showed a neck rather than a face. That's arguably right, but it's a change in behaviour. We haven't switched. Its next test is on full-size scans like the ones your phone takes.

<span class="section-num">09</span>

## The coach: does it do what you ask?

The coach can read your routines, products, progress and diary, and it can propose changes: a new routine, a product added, a weekly step. Proposals arrive as a card, and nothing changes until you tap it. So the exam for the coach is about actions as much as words.

We invented a test user: oily skin, a morning and an evening routine, five products, a few past scans, a diary and one remembered preference. Then we wrote **34 messages** covering everything the coach can do, several phrasings for each. "Can you check my routine?" "Look over my skincare." "What should I change in the evening for my acne?" Every message was sent **twice**, because the coach doesn't always answer the same way, and that's worth measuring too.

<div class="table-wrap">
<table>
<thead><tr><th>Check</th><th class="n">Result</th></tr></thead>
<tbody>
<tr><td>Took the action the message asked for</td><td class="n">42 of 44</td></tr>
<tr><td>Never took an action it shouldn't (nothing changed on "hi" or a question)</td><td class="n">68 of 68</td></tr>
<tr><td>A changing mole always got "please see a doctor"</td><td class="n">every time</td></tr>
<tr><td>Never said "I've added it" for a card you still have to tap</td><td class="n">61 of 68</td></tr>
<tr><td>Took the same actions both times it was asked</td><td class="n">88% of messages</td></tr>
<tr><td>Typical reply / slowest tenth of replies</td><td class="n">5.4 s / 16.5 s</td></tr>
</tbody>
</table>
</div>

The biggest problem isn't the actions, it's the words. **About one reply in ten says "I've set up your routine" or "I've added sunscreen" when it has only proposed it.** The card is there, but if you believe the sentence you might never tap it, and then wonder why your routine didn't change. That's the first coach fix we're making.

The two missed actions were the same message both times: "I want to exfoliate with a BHA twice a week, put it in my routine." Instead of proposing the weekly step, the coach asked a string of screening questions. Sensible caution, but not what was asked. It can do both: propose the step and add the caution.

Speed has a pattern too. A reply is fast when the coach already has what it needs and answers in one go. The slow ones look up data they already have, or run a web search to confirm a well-known product before recommending it. Each costs a few seconds you spend watching dots.

<span class="section-num">10</span>

## How we keep it from sliding back

An exam you sit once is a snapshot. The point is to sit it every time. From now on, any change to how the scan or the coach thinks (its instructions, its model, the spot finder) re-runs the papers it could affect, and is compared with the current standard:

- **Safety checks may not drop at all.** Not by one photo.
- **Everything else may wobble by at most one photo's worth**, because models aren't perfectly repeatable, and a rule tighter than the noise would fail every change.
- **The gap between skin tones must stay under 8 points** and within 3 of where it is now.
- **The same photo must score within 3 points** of itself.
- **Speed and cost may not rise by half.** A better answer that takes twice as long is a different product.

Every result lands on a dashboard where a regression shows at a glance, down to which photo or message changed, and why. Nobody has to remember to look. And no one, including us, may edit the photos, the labels or the standard to make a failing change pass. A new standard is a deliberate decision, written down, never a side effect.

<span class="section-num">11</span>

## Your photos stay out of all of this

A photo of your face is about as personal as data gets. Under European data-protection law (GDPR) it counts as biometric data, and a photo of your skin can also say something about your health. Both are special categories that need the most care. So the testing system is built around one rule:

<p class="pull">A photo goes to exactly one place: the AI model that analyses it. Nowhere else.</p>

- **No user photos are in the exam.** The test set is openly licensed images, a few marketing photos, and three of my own. Even mine are used only when I explicitly say so.
- **Our monitoring and dashboards never receive a photo.** Where a test needs to refer to an image, it stores a fingerprint of it (a short code that identifies the file but can't be turned back into a picture), never the picture. Uploading images is switched off in the monitoring tool itself, and an automated test fails if that ever changes.
- **Crash reports are scrubbed** of request bodies and anything that could carry a photo.
- **On real scans, our automatic checks record a pass or a fail.** Did the result parse? Did it avoid diagnosis words? Did it avoid lightening advice? Your photo is never part of them, and people appear by an internal ID, never by name or email.

The test user the coach talks to is invented from scratch. No real person's routine, diary or messages were used to build it.

<span class="section-num">12</span>

## What this doesn't prove

Thirty-three photos is enough to find problems and nowhere near enough to declare anything safe. A few things to keep in mind:

- **The papers are small.** On 7 healthy faces, one photo is 14 percentage points. Small differences between runs are noise, and we treat them as noise.
- **The labels are ours.** We labelled the photos carefully, but we are not dermatologists. Where we weren't sure, the label says so.
- **Test photos aren't scans.** Most are smaller and differently lit than what your phone takes in our guided scan.
- **Darker skin is under-represented.** 6 of 33 photos. We found the redness problem anyway, which is a reason for more of these photos, not fewer.
- **An AI reviewing an AI can be wrong**, as it was at first. We read what it flags; we don't take its word for it.
- **The coach was tested on one invented person.** Real people write differently, and some of you will find phrasings we didn't think of.

None of this replaces a dermatologist. Dermaglow will always tell you to see one when something looks worrying, and that check passed every time.

<span class="section-num">13</span>

## What's next

1. **The coach stops saying "I've added it"** when it has only proposed something, and proposes weekly steps when asked.
2. **The scan stops reading "no redness" on dark skin as calm skin**, and describes inflammation in the colours it actually shows.
3. **The spot finder on darker skin.** On the clear, darkest-skinned face in the set it counted three spots; on clear lighter faces, two or fewer. Small, but it's the direction that matters.
4. **A bigger, darker exam.** More photos of types V–VI, and a front-facing acne photo for the spot map, which can't yet test active spots.
5. **Full-size scans** for the close-up and cheaper-model questions, which small test photos can't settle.

Each of these will sit the exam before it reaches you. If it makes anything worse, you won't see it.

<div class="method">

**Method notes.** All eight experiments ran on 26 October 2026 against the app's production instructions and models. Photos come from Wikimedia Commons, Openverse and open-access (CC BY) medical papers, each used under its licence with attribution kept alongside it; every file is checked against a stored fingerprint so the exam can't drift silently. "Problems found" is the share of labelled findings the scan reported, averaged per photo. The skin-tone gap is the largest difference between Fitzpatrick groups' average scores on clear skin. The reviewer answers four fixed true/false questions from the written result and the skin type only. The coach was tested against an invented user with every outside lookup (web search, retailers, the database) replaced by fixed answers, so its results don't depend on the internet that day.

Earlier posts: [The Number We Couldn't Show You](/posts/the-number-we-couldnt-show-you/) and [The Breakout Was Real. The Recovery Wasn't.](/posts/the-breakout-was-real/)

</div>
