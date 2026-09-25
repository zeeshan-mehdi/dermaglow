---
title: "Green on the Seventh Try"
description: "Dermaglow is coming to Android. It's building and signing and landing in internal testing right now — and getting there took seven separate failures, not one of which was in the app itself."
pubDate: 2026-09-25
author: "Zeeshan Mehdi"
tags: ["Engineering", "Android"]
heroEmoji: "🤖"
---

<p class="byline-stats">By Zeeshan Mehdi · 25 September 2026 · 7 min read · 7 bugs, 76 lines of build config, 0 lines of app code</p>

Dermaglow is coming to Android. It is not a plan or a roadmap item — the
 app compiles, signs, and uploads itself to Google Play's internal testing
 track on every build we ask for. The thing exists. A handful of people are
 already holding it.

This post is not a countdown. It's the story of the week the build spent
 refusing to exist, because that turns out to be the more interesting half
 — and because the only thing that ever earned trust on this blog is
 showing the failures at the same resolution as the wins.

<span class="section-num">01</span>

## Seven ways to not ship an app

Here is the part nobody puts in a launch announcement. Between "the
 Android code is finished" and "the Android build exists" sat seven
 distinct failures, each of which killed the build stone dead, and each of
 which had to be found by reading a compiler's mind.

None of them were in Dermaglow. Not the scanner, not the models, not the
 routine engine, not a single line of the app's actual behaviour. All seven
 lived in the machinery that turns the code into a file Google will accept.

<figure>
<svg viewBox="0 0 760 330" role="img"
     aria-label="Eight build attempts. Each bar shows how far through the build pipeline the attempt got before it died. The attempts do not get steadily further — the fourth and fifth died earlier than the third.">
  <text x="0" y="14" class="svg-title">How far each attempt got before it died</text>

  <line x1="120" y1="30" x2="120" y2="272" stroke="var(--band)" stroke-width="1"/>
  <line x1="240" y1="30" x2="240" y2="272" stroke="var(--band)" stroke-width="1"/>
  <line x1="380" y1="30" x2="380" y2="272" stroke="var(--band)" stroke-width="1"/>
  <line x1="530" y1="30" x2="530" y2="272" stroke="var(--band)" stroke-width="1"/>
  <line x1="640" y1="30" x2="640" y2="272" stroke="var(--band)" stroke-width="1"/>

  <text x="120" y="292" class="svg-label" text-anchor="middle">configure</text>
  <text x="240" y="292" class="svg-label" text-anchor="middle">resolve</text>
  <text x="380" y="292" class="svg-label" text-anchor="middle">compile</text>
  <text x="530" y="292" class="svg-label" text-anchor="middle">minify</text>
  <text x="640" y="292" class="svg-label" text-anchor="middle">bundle</text>
  <text x="735" y="292" class="svg-label" text-anchor="middle">upload</text>

  <g fill="var(--noise)">
    <rect x="60" y="36"  width="60"  height="13" rx="3"/>
    <rect x="60" y="62"  width="320" height="13" rx="3"/>
    <rect x="60" y="88"  width="470" height="13" rx="3"/>
    <rect x="60" y="114" width="320" height="13" rx="3"/>
    <rect x="60" y="140" width="180" height="13" rx="3"/>
    <rect x="60" y="166" width="470" height="13" rx="3"/>
    <rect x="60" y="192" width="500" height="13" rx="3"/>
  </g>
  <rect x="60" y="222" width="700" height="15" rx="3" fill="var(--signal)"/>

  <text x="0" y="47"  class="svg-label">1 · version floors</text>
  <text x="0" y="73"  class="svg-label">2 · kotlin 1.6</text>
  <text x="0" y="99"  class="svg-label">3 · ML Kit / R8</text>
  <text x="0" y="125" class="svg-label">4 · timezone</text>
  <text x="0" y="151" class="svg-label">5 · jetifier</text>
  <text x="0" y="177" class="svg-label">6 · heap</text>
  <text x="0" y="203" class="svg-label">7 · disk</text>
  <text x="0" y="234" class="svg-strong" fill="var(--signal)">green</text>

  <text x="758" y="234" class="svg-strong" text-anchor="end" fill="var(--paper)">signed .aab</text>
</svg>
<figcaption>**Debugging is not a staircase.** Attempts four and five died
 *earlier* in the pipeline than attempt three did. Fixing the thing that
 breaks at minute nine regularly reveals a thing that breaks at minute two —
 which is why "we're nearly there" is the least reliable sentence in
 software.</figcaption>
</figure>

<span class="section-num">02</span>

## The seven

<div class="table-wrap">
<table>
  <thead><tr><th>#</th><th>what broke</th><th>why it broke</th></tr></thead>
  <tbody>
    <tr><td class="n">1</td><td>Android Gradle Plugin and Kotlin were too old</td><td>Flutter enforces its own version floors, tied to the Flutter version rather than to anything the project declares</td></tr>
    <tr><td class="n">2</td><td>An analytics plugin pinned Kotlin&nbsp;1.6 inside its own build file</td><td>You cannot edit a dependency's source. The fix reaches down from the root build and overrides every subproject's compiler settings at once</td></tr>
    <tr><td class="n">3</td><td>The code shrinker refused to shrink</td><td>Our text-recognition library mentions Chinese, Japanese, Korean and Devanagari recognisers we never ship. R8 sees classes referenced but absent, and stops</td></tr>
    <tr><td class="n">4</td><td>A timezone plugin called an API that no longer exists</td><td>It used Flutter's v1 embedding, deleted from the engine years ago. See below — this is the interesting one</td></tr>
    <tr><td class="n">5</td><td>A compatibility shim choked on Flutter's own engine</td><td><span class="mono">enableJetifier</span> was translating ancient support-library code that nothing in the tree has used for years. Turning it off also made local builds ~20× faster</td></tr>
    <tr><td class="n">6</td><td>The shrinker ran out of memory</td><td>A 1.5&nbsp;GB heap is fine until you have this many plugins. It is not a bug so much as a number that stopped being true</td></tr>
    <tr><td class="n">7</td><td>The build server ran out of disk</td><td>Android's NDK, the SDK platforms and R8's intermediates together exceed the free space on a stock CI runner</td></tr>
  </tbody>
</table>
</div>

Seven fixes, spread across a Gradle settings file, two build files, a
 rules file, one dependency version, two configuration numbers and a CI
 workflow. Seventy-six lines. Not one of them in a `.dart` file — not one
 line of the app's own code changed to make the app run on Android.

<p class="pull">The app was ready. The scaffolding around it wasn't. Those
 are wildly different problems that look identical from the outside, which
 is exactly why "coming soon" drags on for months.</p>

<span class="section-num">03</span>

## The one that only failed on someone else's machine

Number four deserves its own section, because it's the one that could
 still be hiding somewhere.

This Mac is stuck on an old version of Flutter — the laptop's operating
 system is too old to run a newer one, and that ceiling isn't moving until
 the hardware does. Our build server has no such problem and tracks the
 current stable release. So the two disagree, occasionally, about what
 valid code is.

The timezone plugin is exactly that disagreement. It referenced a class
 called `Registrar`, part of an API Flutter removed. The older engine on
 this laptop still carried enough of the old world to tolerate it. The
 newer engine on the server didn't, and said so:
 `Unresolved reference: Registrar`.

So the build passed locally and failed in CI, which is the failure mode
 engineers most love to dismiss as "CI being flaky."

<p class="pull">A local pass is necessary. It is not sufficient. Two of
 these seven bugs were completely invisible on the machine the code was
 written on.</p>

The fix had a trap in it, too. The plugin's current major version renames
 what the function hands back — a plain string becomes a structured object —
 which would mean touching real app code and re-testing every notification
 the app schedules. We took the last version before that break instead.
 Same call sites, same return type, none of the risk. Sometimes the
 disciplined move is the boring one.

<span class="section-num">04</span>

## What Android users actually get

Not a port. Not a stripped-down companion app. The same codebase that
 runs on iPhone, compiled for a different processor.

That means the scanner is the same scanner, calling the same models with
 the same prompts, against the same thresholds we spent two long posts
 interrogating on this blog — including the ±6 band we
 [refused to loosen](/posts/the-number-we-couldnt-show-you/), and the
 [shine blind spot](/posts/the-breakout-was-real/) we found by breaking out
 and measuring it. Android users inherit the honest version of the
 instrument, blind spots documented, on day one.

What that also means, and I'd rather say it here than let someone find
 out the hard way: every caveat in those two posts applies on Android too.
 A different camera stack photographing the same face is a variable we have
 not yet measured, and the moment there are enough Android scans to compare,
 measuring it is the next study. If the numbers diverge, that post gets
 written the same way the others did.

<span class="section-num">05</span>

## Where it is right now, honestly

**Internal testing.** That's a real Google Play track, with a real
 signed build on it, installed on real devices that are not mine.

Between here and a public listing there are three things left, and none
 of them are code: billing has to be wired through Play's own subscription
 products and verified end to end, Google's data-safety declarations have to
 be filled in and be true, and the pre-launch report — Google runs your app
 on a rack of real phones and tells you what it broke — has to come back
 clean on devices we don't own.

I'm not giving you a date. This blog has a rule about claiming things
 before the evidence exists, and it was written after I broke that rule and
 had to
 [publish a correction](/posts/the-breakout-was-real/). A date would be the
 same mistake in a nicer outfit.

What I'll give you instead is this: the build is green, it uploads itself,
 and the only things left are paperwork and other people's phones.

<div class="caveat">

**If you're on iOS**, you don't have to wait for any of this — the app is
 live now, and the two research posts above will tell you more about how its
 number actually behaves than any app-store listing ever would.

**If you're on Android**, the next post on this blog is the one with the
 link in it. There'll be an open testing track before there's a public
 listing, and the people in it will be the first to scan.

</div>

<div class="method">

**Notes.** The seven fixes landed between 23 and 25 September 2026 as
 seven commits touching `android/settings.gradle`, `android/build.gradle`,
 `android/app/build.gradle`, a new `android/app/proguard-rules.pro`,
 `pubspec.yaml`, `android/gradle.properties` and
 `.github/workflows/android_build.yml`. The release bundle is signed with an
 upload key held only by CI; Play re-signs with its own key on the way to
 devices. The internal-testing upload runs through a service account scoped
 to testing-track releases only, deliberately separate from the one our
 billing provider uses — if either credential leaks, the blast radius is
 one job, not the account.

The line counts in this post are diff line counts, taken from the commits
 themselves rather than from memory. The one time this blog quoted a number
 from memory instead of from the source, it was wrong, and it got its own
 correction box.

</div>
