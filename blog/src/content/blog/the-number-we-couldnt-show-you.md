---
title: "The Number We Couldn't Show You"
description: "I spent a week testing whether our own Skin Score can actually see a spot appear. It can. It just can't say so — and working out why changed what we're building next."
pubDate: 2026-09-05
author: "Zeeshan Mehdi"
tags: ["Engineering", "Research"]
heroEmoji: "📉"
---

<p class="method" style="border-top:none;padding-top:0;margin-top:0;">49 photographs · 156 model calls · $5.45 · 12 min read</p>

<figure>
<svg viewBox="0 0 760 300" role="img"
           aria-label="Eight real skin changes, all correctly signed, all sitting inside the plus or minus six point noise band. A control with no real change moved further than any of them.">
        <text x="0" y="14" class="svg-title">How far the Skin Score moved on eight real skin changes</text>

        <!-- noise band -->
        <rect x="40" y="40" width="680" height="150" fill="var(--band)" rx="3"/>
        <text x="48" y="58" class="svg-label">the ±6 point band — anything in here, the app must call &ldquo;no change&rdquo;</text>

        <!-- zero line -->
        <line x1="380" y1="34" x2="380" y2="228" stroke="var(--ink-3)" stroke-width="1"/>
        <text x="380" y="246" class="svg-label" text-anchor="middle">0</text>
        <text x="40"  y="246" class="svg-label">−6</text>
        <text x="720" y="246" class="svg-label" text-anchor="end">+6</text>
        <text x="150" y="266" class="svg-label">skin got worse</text>
        <text x="610" y="266" class="svg-label" text-anchor="end">skin got better</text>

        <!-- 8 real changes: x = 380 + delta*56.67 -->
        <g>
          <circle cx="153" cy="62"  r="6" fill="var(--signal)"/><text x="167" y="66" class="svg-strong">−4.0</text>
          <circle cx="153" cy="86"  r="6" fill="var(--signal)"/><text x="167" y="90" class="svg-strong">−4.2</text>
          <circle cx="210" cy="110" r="6" fill="var(--signal)"/><text x="224" y="114" class="svg-strong">−3.0</text>
          <circle cx="340" cy="134" r="6" fill="var(--signal)"/><text x="354" y="138" class="svg-strong">−0.7</text>
          <circle cx="448" cy="158" r="6" fill="var(--signal)"/><text x="400" y="162" class="svg-strong" text-anchor="end">+1.2</text>
          <circle cx="607" cy="182" r="6" fill="var(--signal)"/><text x="593" y="186" class="svg-strong" text-anchor="end">+4.0</text>
          <circle cx="607" cy="206" r="6" fill="var(--signal)"/><text x="593" y="210" class="svg-strong" text-anchor="end">+4.0</text>
          <circle cx="641" cy="230" r="6" fill="var(--signal)"/><text x="627" y="234" class="svg-strong" text-anchor="end">+4.6</text>
        </g>

        <!-- the control -->
        <circle cx="652" cy="22" r="6" fill="var(--noise)"/>
        <text x="638" y="26" class="svg-strong" text-anchor="end" fill="var(--noise)">+4.8 — skin that did not change at all</text>
      </svg>
<figcaption>Every green dot is a real change — a spot that appeared or cleared, confirmed by the person in the photographs. Every one is on the correct side of zero. Not one is far enough from zero for the app to be allowed to mention it. The red dot is a control: two photographs taken three seconds apart, where nothing could possibly have changed. It moved further than any of the real ones.</figcaption>
</figure>

<span class="section-num">01</span>

## Every skin app shows you a number. Almost nobody checks it.

Open any AI skincare app and you get a score. 78 today, 82 last week — look, you're improving. The number is the product. It's what makes the app feel like a measurement instead of a mirror.

So here's a question worth asking about ours, and about everyone else's: if you photographed the same face twice, minutes apart, would the number stay the same? And the harder one: if a spot actually appeared, would the number notice?

We went looking for whether anyone had published an answer. A 2025 systematic review examined 29 papers on AI acne grading. Not one of them measured test–retest reproducibility. The review's own conclusion is that no published algorithm has demonstrated it. And we could not find a single study anywhere evaluating whether a vision model can detect *change over time* in skin photographs.

<p class="pull">The thing every skin app sells is change over time. The thing nobody has measured is change over time.</p>

So we measured ours. Here is everything we found, including the parts that make us look bad.

<span class="section-num">02</span>

## What we actually did

I contributed 49 photographs of my own face from my camera roll — fourteen months, twenty-one separate sittings, one phone. Not studio shots. Ordinary selfies in bathrooms, parks, barbershops, offices. The photographs a real user would actually take.

Then I went through every one and marked where the spots were, and which dates I'd describe as breaking out. That last part matters: it is the only ground truth in the whole exercise that is not an AI's opinion. It also caught real errors — twice I found the model being asked about the wrong cheek, which would have scored a correct answer as a failure.

From that we built two kinds of test pair:

**Real changes.** Eight before-and-after pairs where something genuinely happened — a breakout appeared on his forehead, a cluster of spots on his cheek cleared up. The model should see these.

**Non-changes.** Pairs taken within a single sitting, seconds to minutes apart. Skin cannot change in ninety seconds. Anything the model reports here is invented.

That second category is the one most benchmarks skip, and it's the one that matters most. Detection rate on its own always flatters. The nearest published study to ours — smartphone detection of skin changes, 2024 — reported 92% sensitivity and 95.5% specificity, which sounds excellent until you notice that only 38% of the changes it flagged were real. When genuine change is rare, a small false-positive rate drowns the true signal.

<span class="section-num">03</span>

## Finding one: it can see

Our comparison model caught **six of the eight real changes**, giving the same answer three times out of three each time.

One result mattered more than the count. Two of the pairs are the same two photographs handed over in opposite order. A model that's secretly guessing from position — "the second photo is probably worse" — scores them identically. A model actually looking at skin flips its answer. Ours flipped, exactly: −1 −1 −1 one way, +1 +1 +1 the other.

Of the two it missed, one wasn't really a miss. It spotted the lesion and filed it under *flat mark* rather than *raised spot* — a filing error, not blindness.

<div class="caveat">

**The honest caveat.** Eight pairs from one person is a smoke test, not a validation. Six out of eight sounds like 75%, but the true rate could be anywhere from 41% to 93%. We're reporting it because the alternative outcome — catching none of them — would have been decisive, and it didn't happen. That's worth knowing. A precise number isn't available at this size and we're not going to pretend otherwise.

</div>

<span class="section-num">04</span>

## Finding two: it also sees things that aren't there

Across pairs of photographs taken in the same sitting — same room, same light, same minute, same face — the model reported a change **roughly a third of the time**.

32% in one run of 22 pairs. 33% in an earlier run using different sittings and a different construction. That number is stubborn.

The worst cases are the most similar photographs. Two frames taken 56 and 108 seconds apart, both straight-on, both in the same bathroom, came back "more inflammatory spots" — three times out of three, with complete confidence.

We've spent weeks trying to find out why, by changing one thing at a time on real photographs:

| Suspect | How we tested it | Verdict |
| --- | --- | --- |
| Brightness | same photo, relit across the full range users produce | ruled out |
| Colour of the light | warm bulb vs daylight, 3× the real-world range | ruled out |
| How close you hold the phone | same photo, 1.0× to 1.75× face size | ruled out |
| Which part of the face is framed | crop moved up, down, left, right | ruled out |
| Head angle | 22 same-sitting pairs, half turning the head | ruled out |

That last one was our leading theory, and we were confident about it. There's published work showing camera angle shifts measured skin colour while distance doesn't, and we'd seen a striking case: two profile shots three seconds apart, model insisting the redness had changed.

We ran the test properly. Pairs where the head turned misfired *less* than pairs where it didn't — **27% against 36%**. Our theory was wrong. The striking case was a coincidence we'd built a story around.

We still don't know the cause. What's left is expression, the shine of sebum on skin, and plain sensor noise at the scale of a five-millimetre spot. We'll keep going.

<span class="section-num">05</span>

## Finding three: the number was right every single time — and we still couldn't show it to you

Everything above is about a comparison model that runs quietly in the background. The last test is about the Skin Score itself. The number on your screen.

We ran it over the same eight real changes to my skin. Not one of them moved the score by more than six points, which is our threshold for saying anything at all. By the rule we'd written, the answer on all eight was "no measurable change."

Then we looked at the direction of each movement.

<figure>
<svg viewBox="0 0 700 150" role="img"
           aria-label="All eight changes moved the correct way: the four that got worse pushed the score down, the four that improved pushed it up.">
        <text x="0" y="14" class="svg-title">Direction of movement on eight real changes</text>
        <line x1="350" y1="30" x2="350" y2="110" stroke="var(--ink-3)" stroke-width="1"/>
        <text x="350" y="128" class="svg-label" text-anchor="middle">no movement</text>
        <text x="120" y="128" class="svg-label" text-anchor="middle">score fell</text>
        <text x="580" y="128" class="svg-label" text-anchor="middle">score rose</text>
        <g fill="var(--signal)">
          <rect x="123" y="34" width="227" height="12" rx="3"/>
          <rect x="112" y="52" width="238" height="12" rx="3"/>
          <rect x="180" y="70" width="170" height="12" rx="3"/>
          <rect x="310" y="88" width="40"  height="12" rx="3"/>
          <rect x="350" y="34" width="227" height="12" rx="3" opacity=".92"/>
          <rect x="350" y="52" width="227" height="12" rx="3" opacity=".92"/>
          <rect x="350" y="70" width="261" height="12" rx="3" opacity=".92"/>
          <rect x="350" y="88" width="68"  height="12" rx="3" opacity=".92"/>
        </g>
        <text x="0" y="46"  class="svg-label">breakout appeared</text>
        <text x="0" y="64"  class="svg-label">spots appeared</text>
        <text x="0" y="82"  class="svg-label">breakout appeared</text>
        <text x="0" y="100" class="svg-label">pimple appeared</text>
        <text x="700" y="46"  class="svg-label" text-anchor="end">breakout cleared</text>
        <text x="700" y="64"  class="svg-label" text-anchor="end">breakout cleared</text>
        <text x="700" y="82"  class="svg-label" text-anchor="end">cluster cleared</text>
        <text x="700" y="100" class="svg-label" text-anchor="end">spots cleared</text>
      </svg>
</figure>

**Eight out of eight, correct.** Every time his skin got worse the score went down. Every time it cleared, the score went up. A number generating noise gets that right half the time; the odds of a clean sweep by luck are under one in a hundred.

<p class="pull">The signal is real. It is simply quieter than the noise sitting on top of it — so we built a rule that silences it, and the rule is correct.</p>

Three numbers explain the whole situation:

| What | Points |
| --- | --- |
| Score wobble when we re-score the identical image file | 2.6 |
| How much a real breakout actually moves the score | 3.2 |
| Wobble between photographs taken on different days | 6.0 |

The effect we want to report is bigger than the model's own inconsistency and smaller than the variation introduced between one day's photograph and the next. Everything in the gap between 2.6 and 6.0 is not skin. It's the light in your bathroom, how close you held the phone, what time of day it was, whether you'd just washed your face.

Close that gap and a real breakout becomes reportable. That's a camera problem, not an AI problem — which is good news, because camera problems have known fixes.

<span class="section-num">06</span>

## What changes because of this

**We're going to average your scans.** Three scans over three days, treated as one reading, cuts the noise by about 40% — taking that ±6 band down to roughly ±3.5, which is under the size of a real breakout. This is the single highest-value change available and it needs no new model. It's how a 2026 psoriasis trial got patient smartphone photos to agree with in-person physician assessment.

**Guided capture.** Framing and distance guidance at the moment you take the photo, so consecutive scans are more alike. We've already shipped the measurement side of this — the app now records how your face was framed on every scan, which is what lets us tune the guidance against real data rather than guesses.

**A nudge toward a consistent time of day.** Skin oil follows a daily cycle that peaks in the early afternoon. A morning scan and an evening scan are not the same measurement.

**We're not loosening the threshold.** The tempting move is to lower the bar so the app says more. We're not doing that. The band exists because telling you your skin improved when it didn't is the worst thing this product can do. We'll earn a smaller band by taking better photographs, not by lowering the standard for what counts as evidence.

<span class="section-num">07</span>

## Why we're publishing our own bad numbers

A 33% false-positive rate is not a good result. We could have run this quietly, fixed what we could, and said nothing.

Two reasons we didn't.

The first is that **you can't check any of this yourself.** When an app tells you your skin improved 4%, you have no way of knowing whether that's your skin or the weather. The only protection you have is whether the people building it went looking for the answer and told you what they found.

The second is that the honest comparison isn't as damning as it sounds. Trained dermatologists grading acne severity from photographs agree with each other only moderately — inter-rater agreement in the published studies runs from poor to fair. Judging skin from a photo is genuinely hard, for people too. The problem isn't that AI is uniquely bad at it. The problem is that AI reports a confident number to two decimal places while a dermatologist would shrug and say "looks about the same."

<p class="pull">We'd rather build the thing that shrugs accurately than the thing that's confidently wrong.</p>

<span class="section-num">08</span>

## What this doesn't prove

One person. One skin tone. One phone. Forty-nine photographs and eight real changes.

Mine. That's enough to find problems and nowhere near enough to declare anything safe. Every number here would need a proper study across many people and skin tones before it meant anything general — and the published literature is clear that erythema in particular is harder to see on darker skin under ordinary photography, so a result from one light-brown face tells you very little about anyone else's.

And the labels are my own read of my face, not a dermatologist's. Where I was not sure, I have said so.

What we'd claim is narrower: on this face, with these photographs, the instrument sees real change and reports change that isn't there at about a third the rate — and the score's true signal is currently smaller than the noise our own capture process introduces.

That's enough to know what to build next.

<div class="method">

**Method notes.** Comparison model claude-opus-5; Skin Score from gemini-3.6-flash, the model that runs on real scans. Every test used the exact prompts the production app uses. Three to five repeats per judgement at temperature 0. Confidence intervals are Wilson; the direction result is an exact sign test (p = 0.0078). The ±6 figure is a Bland–Altman repeatability coefficient, 2.77 × within-subject standard deviation.

The photographs are mine and stay in a private repository. Photographs of anyone else who turned up in the camera roll — a friend in two frames, bystanders at an event in four — were deleted rather than labelled. They were never mine to hand to a third-party model, and a note saying "do not use" is not a safeguard against a script that reads the whole folder.

If you're doing similar work and want the detail, we're happy to share the method. The one thing we'd urge: include the pairs where nothing happened. It's the half of the test that tells you the truth.

</div>
