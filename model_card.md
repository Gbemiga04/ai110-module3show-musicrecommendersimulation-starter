# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MoodMatch 1.0**: a small recommender that picks songs by how you want to *feel* first.

---

## 2. Intended Use  

**Goal / task:** MoodMatch suggests the top 5 songs from a small catalog that best fit one listener's taste. It doesn't predict whether you'll *like* a song. It scores how closely each song matches the mood, energy, genre and sound you asked for, then ranks them.

**Assumptions about the user:** it assumes you can describe your taste with one mood, one genre, one energy level (0 to 1) and whether you like acoustic music. It also assumes your taste stays the same and doesn't depend on time of day or activity.

**Intended use:**
- Classroom exploration of how recommender systems turn data into rankings.
- Experimenting with weights and user profiles to see how results change.
- Showing why each song was picked, through the list of reasons next to each score.

**Not intended for:**
- Real users or a real music app. The catalog has only 18 songs, and most moods appear once.
- Judging songs or artists as "good" or "bad." A low score only means a song doesn't match one profile.
- Users whose taste mixes moods or genres, or anyone who types labels differently (for example "Chill" instead of "chill"), since matching is exact.
- Any decision that matters, like what music gets promoted or paid. The labels were written by hand and partly generated with AI, so they are subjective.

---

## 3. How the Model Works  

Imagine a judge with a scorecard who looks at every song, one at a time:

- **Does the song have the mood you want?** That's worth the most, 2 points. I made mood the biggest factor because I pick music by how I want to feel.
- **Is the song about as energetic as you want?** Up to 1.5 points. A perfect match gets all 1.5, and the further off it is (too calm *or* too intense), the fewer points it gets. Louder isn't automatically better.
- **Is it your genre?** 1 point.
- **Does it sound the way you like, acoustic or electronic?** Up to half a point.

The best possible score is 5. After every song is scored, the judge sorts them from highest to lowest and shows the top 5, along with the reasons each song earned its points. If two songs tie, the one closer to your energy level wins.

**What I changed from the starter logic:** the suggested starting point gave genre 2 points and mood 1. I flipped them, because genre-first ranked a lofi song in the wrong mood above an ambient song in the right mood, and that didn't match how I actually choose music. I also added the acoustic preference and the energy tie-breaker.

---

## 4. Data  

- **Size:** 18 songs in `data/songs.csv`. The starter had 10; I added 8.
- **Features per song:** title, artist, genre, mood, energy, tempo, valence (how happy it sounds), danceability and acousticness. The scoring uses only mood, energy, genre and acousticness. Tempo and danceability rise and fall almost exactly with energy, so using them would count the same thing twice.
- **What's represented:** 15 genres (lofi, pop, rock, ambient, jazz, synthwave, indie pop, hip-hop, blues, classical, metal, country, r&b, edm, reggae) and 14 moods. The 8 songs I added brought in new genres and moods, including sad and angry songs. The original 10 had nothing sad.
- **Limits:**
  - The catalog is tiny and uneven. Lofi and "chill" have 3 songs each, while most genres and moods have just 1.
  - Only 5 songs have energy above 0.8.
  - There are no sad-and-energetic songs and no calm-and-angry songs.
  - Missing parts of taste: lyrics, language, vocals vs instrumental, era, and culture-specific genres. The songs and artists are made up.

---

## 5. Strengths  

- **Clear-cut profiles work well.** Happy Pop, Chill Lofi and Deep Intense Rock each get the obvious best song at #1 (Sunrise City, Library Rain and Storm Runner), with scores near the 5.0 maximum.
- **It tells opposite tastes apart.** Chill Lofi and Deep Intense Rock get completely different lists. The top song for one ranks around 15th for the other.
- **"Closeness" scoring for energy works.** Calm listeners aren't pushed toward the loudest songs, which would happen if higher energy simply scored higher.
- **Mood-first allows some discovery.** A chill listener gets a chill *ambient* track (Spacewalk Thoughts) ahead of a lofi song in the wrong mood, which matched my intuition.
- **Every result explains itself.** Each recommendation lists exactly where its points came from, so it's easy to see why a song ranked where it did, and to spot when something is off.

---

## 6. Limitations and Bias 

The biggest weakness I found is that mood, my heaviest weight at +2.0, only counts when the label matches exactly, and 11 of the catalog's 14 moods appear on just one song. Listeners whose mood is rare or slightly differently named get at most one strong match, and the rest of their list is filled by energy alone. For example, a Deep Intense Rock listener sees a pop workout track ranked 2nd while the metal song Iron Verdict ranks 4th, because "angry" earns zero credit toward "intense," and a chill listener never gets the mood bonus for "relaxed" jazz that fits perfectly. This creates a filter bubble that favors users with common moods like "chill" (3 songs), while users who want sad, angry or romantic music are underserved. The system also never tells users when nothing fits; "Unknown Tastes" still gets five confident-looking recommendations scoring only about 1.7 out of 5.

**Other biases I found:**

- **Energy gap favors extremes.** Because energy is scored by distance, a user targeting 0.5 can never be more than 0.5 away from any song, so energy points for the whole catalog only range from 0.80 to 1.47. For a 0.1 or 0.95 user they range across about 1.2 points. Mid-energy listeners therefore get flatter, less distinctive lists: the "Unknown Tastes" top 5 are separated by only 0.2 points.
- **Acoustic preference is drowned out.** Energy and acousticness are almost perfect opposites in this data, so an "acoustic metal" fan gets the same list as any metal fan.
- **Strict labels and no input checks.** "indie pop" gets no credit as "pop," capitalized input like "Chill" matches nothing, and an energy target outside 0–1 produces negative points.

---

## 7. Evaluation  

I stress-tested the recommender with seven user profiles defined in `src/main.py`: three "normal" listeners and four adversarial or edge-case profiles meant to trick the scoring logic. For each one I ran `python -m src.main` and checked whether the top 5 made sense to me as a listener.

| Profile | Type | What it tests | #1 result | Verdict |
|---|---|---|---|---|
| Happy Pop | Normal | Starter profile | Sunrise City (4.88) | As expected |
| Chill Lofi | Normal | My own taste | Library Rain (4.85) | As expected |
| Deep Intense Rock | Normal | Opposite of Chill Lofi | Storm Runner (4.93) | As expected, but metal ranks only 4th |
| Sad but Hyped | Adversarial | Sad mood + 0.9 energy (conflict) | Empty Platform (3.73) | Mood wins; slots 2–5 are happy/intense songs |
| Acoustic Headbanger | Adversarial | Metal + likes acoustic (conflict) | Iron Verdict (4.48) | Acoustic preference silently ignored |
| Unknown Tastes | Adversarial | Genre/mood not in catalog | Silk Afterglow (1.72) | Pure energy ranking, all scores low |
| Sloppy Input | Adversarial | "Chill"/"Lofi" capitalized, energy 1.5 | Iron Verdict (0.72) | Broken: a chill fan gets metal |

### What I observed

- **Normal profiles work.** Each gets a top result that matches both labels, and Chill Lofi vs Deep Intense Rock produce nearly opposite lists.
- **Mood dominates conflicts.** For "Sad but Hyped," the one sad song wins even though its energy (0.30) is far from 0.9. After that, the list is filled with intense and euphoric songs, which match the energy but not the sadness. The system can't find a song that's sad *and* energetic because none exist, and it doesn't say so.
- **Weak preferences get drowned out.** "Acoustic Headbanger" gets almost the same list as a non-acoustic metal fan. Acoustic fit is worth only 0.5 points, and every high-energy song in the catalog is electronic, so the preference has no real effect.
- **No matches means energy decides.** "Unknown Tastes" gets r&b, country and reggae purely because their energy is near 0.5. Scores top out at 1.72 / 5.0, a sign that nothing really fits, but the output still presents them as recommendations.
- **Input isn't validated (real bugs).**
  - Matching is case-sensitive, so "Chill" ≠ "chill" and "Lofi" ≠ "lofi". The user loses all 3 points from label matches.
  - An energy target of 1.5 is accepted. Low-energy songs then get *negative* energy points, and the reason text prints as "+-0.48" (for example, Moonlit Sonata scores 0.005).
  - A chill lofi fan who typed their profile slightly wrong ends up with metal and EDM.
- **Ties are handled.** In "Sad but Hyped," Storm Runner and Gym Hero both score 1.93, and the energy-closeness tie-breaker puts Storm Runner first (0.91 is closer to 0.9 than 0.93).

### Accuracy and surprises

**Why Storm Runner ranked #1 for Deep Intense Rock.** It is the only song that earns every bonus: mood "intense" (+2.0), genre "rock" (+1.0), energy 0.91 vs target 0.90 (+1.48), and low acousticness (+0.45), for 4.93 out of 5.0. The runner-up, Gym Hero, also matches "intense" and is almost as energetic, so the 1.0-point gap between them is basically the genre bonus.

**What felt wrong:** Gym Hero (a pop workout track) comes 2nd, while Iron Verdict (metal, energy 0.97) comes only 4th with 1.88, behind an EDM song. To a rock fan, metal is much closer than pop. The cause is exact-match mood: Iron Verdict is labeled "angry," not "intense," so it misses the 2.0-point mood bonus, and "metal" doesn't count as "rock." The weights are working as designed, but the labels are too literal to capture that angry metal and intense rock feel similar.

**Does one song dominate every list?** No. Six different songs take #1 across the seven profiles, so the genre weight isn't overpowering. But Gym Hero shows up in 5 of 7 top-5 lists, and Storm Runner, Pulse Horizon, Iron Verdict and Sunrise City show up in 4 each. That repetition comes from **energy plus a small catalog**, not genre: four of my profiles target energy 0.8 or higher, and only five songs in the catalog are that energetic, so whenever labels don't match, the same high-energy songs fill the remaining slots.

### Logic experiment: weight shift

**Change:** I temporarily doubled the energy weight (1.5 → 3.0) and halved the genre weight (1.0 → 0.5), leaving mood (2.0) and acoustic fit (0.5) the same. The maximum score became 6.0 instead of 5.0, which I updated in `main.py` so scores still read correctly. The math stays valid: for any energy target between 0 and 1, energy points stay between 0 and 3.0 and can't go negative. Then I put the original weights back.

**Prompt used:** "In recommender.py, double the energy weight from 1.5 to 3.0 and halve the genre bonus from 1.0 to 0.5. Update the reason text and MAX_SCORE to match. Check that the score still can't go below 0 or above the new maximum for valid inputs."

| Profile | Original top 5 | With the weight shift | Changed? |
|---|---|---|---|
| Happy Pop | Sunrise City, Rooftop Lights, Gym Hero, Concrete Crown, Night Drive Loop | Same order | No |
| Chill Lofi | **Library Rain**, Midnight Coding, Spacewalk, Focus Flow, Coffee Shop | **Midnight Coding**, Library Rain, ... | #1 and #2 swap |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Horizon, Iron Verdict, Sunrise City | Same order | No |
| Sad but Hyped | Empty Platform (3.73), then Storm Runner (1.93) | Empty Platform (3.83), then Storm Runner (3.42) | Same order, but the lead shrinks from 1.80 to 0.41 |
| Acoustic Headbanger | Iron Verdict, Pulse Horizon, Gym Hero, Storm Runner, Sunrise City | Same order | No |
| Unknown Tastes | ..., Midnight Coding, **Concrete Crown** | ..., Midnight Coding, **Focus Flow** | #5 changes |
| Sloppy Input | Iron Verdict, Pulse Horizon, Gym Hero, Storm Runner, Sunrise City | Same order | No |

Chill Lofi output with the weight shift:

```
Profile: Chill Lofi
  mood=chill  genre=lofi  energy=0.4  likes_acoustic=True
================================================================
1. Midnight Coding - LoRoom
   Score: 5.79 / 6.0   (lofi, chill)
     - mood match: chill (+2.0)
     - energy 0.42 vs target 0.40 (+2.94)
     - genre match: lofi (+0.5)
     - acoustic sound (+0.35)

2. Library Rain - Paper Lanterns
   Score: 5.78 / 6.0   (lofi, chill)
     - mood match: chill (+2.0)
     - energy 0.35 vs target 0.40 (+2.85)
     - genre match: lofi (+0.5)
     - acoustic sound (+0.43)

3. Spacewalk Thoughts - Orbit Bloom
   Score: 5.10 / 6.0   (ambient, chill)
     - mood match: chill (+2.0)
     - energy 0.28 vs target 0.40 (+2.64)
     - acoustic sound (+0.46)

4. Focus Flow - LoRoom
   Score: 3.89 / 6.0   (lofi, focused)
     - energy 0.40 vs target 0.40 (+3.00)
     - genre match: lofi (+0.5)
     - acoustic sound (+0.39)

5. Coffee Shop Stories - Slow Stereo
   Score: 3.35 / 6.0   (jazz, relaxed)
     - energy 0.37 vs target 0.40 (+2.91)
     - acoustic sound (+0.45)
```

**More accurate, or just different?** Mostly just different. Five of seven profiles kept the exact same top 5, so the system isn't very sensitive to these weights. The changes that did happen were small:
- Midnight Coding overtook Library Rain by 0.01 because its energy is slightly closer to target. That's a coin flip, not an improvement.
- For Unknown Tastes, Focus Flow (energy 0.40) replaced Concrete Crown (energy 0.78), which is arguably a better fit for someone wanting 0.5 energy.

The bigger effect is hidden in the scores: the system becomes **more fragile**. In Sad but Hyped, the one sad song's lead dropped from 1.80 points to 0.41, so a slightly more energetic non-sad song would now beat the only song that matches the requested feeling. Genre also became almost meaningless. Being the right genre (+0.5) is now worth less than being 0.17 closer in energy. I kept the original weights because they let mood and genre still matter, and the experiment didn't fix the real problem, which is exact-match labels, not weights.

### Why "Gym Hero" keeps showing up (plain-language version)

Think of the recommender as a judge giving each song points on a scorecard: 2 points if the song has the feeling you asked for, up to 1.5 points for being about as energetic as you want, 1 point for being your genre, and a half point for sounding the way you like (acoustic or electronic). For a Happy Pop listener, Gym Hero is a pop song and is about as energetic as they asked for, so it collects the genre point and nearly all the energy points. It's labeled "intense" rather than "happy," so it misses the biggest prize, which is why it lands 3rd and not 1st. It keeps showing up across many lists because it's one of only five really high-energy songs in the catalog: anyone who asks for high energy and doesn't get an exact mood match ends up with Gym Hero filling a slot. It isn't that the system loves Gym Hero; the catalog just doesn't have many other songs to offer energetic listeners.

### Comparing profiles pair by pair

Each comment explains what changed between two profiles' top 5 and whether it makes sense.

**Normal vs normal**

- **Happy Pop vs Chill Lofi:** No songs in common. Happy Pop gets bright, energetic, electronic songs, and Chill Lofi gets quiet, acoustic study tracks. This makes sense because they disagree on every setting: mood, genre, energy (0.8 vs 0.4) and acoustic.
- **Happy Pop vs Deep Intense Rock:** They share Gym Hero and Sunrise City because both want high energy and electronic sound. The order flips: Sunrise City is #1 for Happy Pop (happy + pop) but only #5 for rock, while Gym Hero rises to #2 for rock because its "intense" mood now matches. Same songs, different feeling, different ranking. That's valid.
- **Chill Lofi vs Deep Intense Rock:** No overlap, and the lists are nearly mirror images: Library Rain is 1st for Chill Lofi and 15th for rock, and Storm Runner is the reverse. This is the clearest proof the system can tell calm from loud.

**Normal vs adversarial**

- **Happy Pop vs Sad but Hyped:** Both want high energy, so they share Gym Hero. But Sad but Hyped's #1 is a slow blues song, because the sad-mood points (2.0) outweigh the energy points it loses. Asking for a different feeling changed the top pick even though energy was similar.
- **Happy Pop vs Acoustic Headbanger:** They share Gym Hero and Sunrise City, two energetic songs. The headbanger's #1 is metal because of its angry mood and genre, but asking for "acoustic" didn't pull in any quieter songs. All the energetic songs are electronic, so the half point for acoustic sound can't change anything.
- **Happy Pop vs Unknown Tastes:** Only Concrete Crown overlaps. Unknown Tastes asks for middle energy (0.5), so it gets mid-tempo r&b, country and reggae instead of upbeat pop. With no mood or genre matches, energy alone decides, which is why its scores are so much lower.
- **Happy Pop vs Sloppy Input:** They share Gym Hero and Sunrise City, but for different reasons. Sloppy Input asked for impossible energy (1.5), so the system simply picks the most energetic songs. It's a valid result for the numbers given, but not what a "chill lofi" user meant.
- **Chill Lofi vs Sad but Hyped:** No overlap. Even though Empty Platform (sad blues) is low-energy like the chill songs, Chill Lofi wants a "chill" mood and Sad but Hyped wants high energy for everything after #1, so the lists diverge completely.
- **Chill Lofi vs Acoustic Headbanger:** No overlap, even though both like acoustic sound. The acoustic half point is too small to compete with mood and energy, so this shared preference has no visible effect.
- **Chill Lofi vs Unknown Tastes:** They share Midnight Coding, which has energy 0.42, close to both targets (0.4 and 0.5). Chill Lofi ranks it 2nd because of mood and genre matches, while Unknown Tastes ranks it 4th on energy alone. Same song, but for very different reasons.
- **Chill Lofi vs Sloppy Input:** This is the most important comparison. Sloppy Input was *meant* to be Chill Lofi with typos ("Chill," "Lofi," energy 1.5), yet the two lists share nothing: Chill Lofi gets lofi, and Sloppy Input gets metal and EDM. Small input mistakes completely break the results, so the system needs input cleanup.
- **Deep Intense Rock vs Sad but Hyped:** They share four of five songs (Storm Runner, Gym Hero, Pulse Horizon, Iron Verdict). Both want energy around 0.9 and electronic sound, and once Sad but Hyped's one sad song is used up, it falls back on the same loud songs. This shows energy filling the gaps when moods run out.
- **Deep Intense Rock vs Acoustic Headbanger:** Same five songs in a different order. Iron Verdict jumps from 4th to 1st because it matches "angry" and "metal." Pulse Horizon, Gym Hero and Storm Runner stay clustered because their energy is near 0.95. This makes sense: both are loud-music fans who disagree only on mood and genre labels.
- **Deep Intense Rock vs Unknown Tastes:** No overlap. Rock wants 0.9 energy, and Unknown Tastes wants 0.5, so they pull from opposite parts of the catalog.
- **Deep Intense Rock vs Sloppy Input:** The same five songs again. The broken 1.5 energy target acts like "as loud as possible," which naturally lands on the same high-energy group a rock fan gets.

**Adversarial vs adversarial**

- **Sad but Hyped vs Acoustic Headbanger:** They share four of five songs but have different #1s (sad blues vs angry metal). Each profile's #1 is its one exact mood match, and everything after it is the high-energy pool. A matched mood picks #1, and energy picks the rest.
- **Sad but Hyped vs Unknown Tastes:** No overlap. Both get mostly energy-based lists, but at different targets (0.9 vs 0.5), so they draw from different songs.
- **Sad but Hyped vs Sloppy Input:** Four shared songs. Both end up ranking the loudest songs, one because its mood ran out and the other because its labels didn't match and its energy target was impossible.
- **Acoustic Headbanger vs Unknown Tastes:** No overlap, for the same reason as above: high vs middle energy.
- **Acoustic Headbanger vs Sloppy Input:** **Identical lists in the same order.** Neither profile's acoustic preference matters, and both effectively ask for maximum energy. Two very different "users" getting the exact same recommendations is a clear sign the energy score is doing most of the work.
- **Unknown Tastes vs Sloppy Input:** No overlap. Both get zero label matches, but Unknown Tastes asks for middle energy and Sloppy Input for maximum energy, so energy splits them.

**Overall takeaway:** when mood and genre match, the system behaves sensibly and profiles look clearly different. When they don't, energy takes over, and many different users collapse onto the same handful of loud songs.

### Terminal output for each profile

*These outputs were captured before I added the diversity penalty and summary table (see Stretch Challenges in the README), so they show the original ranking.*

#### Happy Pop

```
================================================================
Profile: Happy Pop
  mood=happy  genre=pop  energy=0.8  likes_acoustic=False
================================================================
1. Sunrise City - Neon Echo
   Score: 4.88 / 5.0   (pop, happy)
     - mood match: happy (+2.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - genre match: pop (+1.0)
     - electronic sound (+0.41)

2. Rooftop Lights - Indigo Parade
   Score: 3.77 / 5.0   (indie pop, happy)
     - mood match: happy (+2.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - electronic sound (+0.33)

3. Gym Hero - Max Pulse
   Score: 2.78 / 5.0   (pop, intense)
     - energy 0.93 vs target 0.80 (+1.30)
     - genre match: pop (+1.0)
     - electronic sound (+0.47)

4. Concrete Crown - Blockwise
   Score: 1.91 / 5.0   (hip-hop, confident)
     - energy 0.78 vs target 0.80 (+1.47)
     - electronic sound (+0.44)

5. Night Drive Loop - Neon Echo
   Score: 1.81 / 5.0   (synthwave, moody)
     - energy 0.75 vs target 0.80 (+1.42)
     - electronic sound (+0.39)
```

#### Chill Lofi

```
================================================================
Profile: Chill Lofi
  mood=chill  genre=lofi  energy=0.4  likes_acoustic=True
================================================================
1. Library Rain - Paper Lanterns
   Score: 4.85 / 5.0   (lofi, chill)
     - mood match: chill (+2.0)
     - energy 0.35 vs target 0.40 (+1.42)
     - genre match: lofi (+1.0)
     - acoustic sound (+0.43)

2. Midnight Coding - LoRoom
   Score: 4.82 / 5.0   (lofi, chill)
     - mood match: chill (+2.0)
     - energy 0.42 vs target 0.40 (+1.47)
     - genre match: lofi (+1.0)
     - acoustic sound (+0.35)

3. Spacewalk Thoughts - Orbit Bloom
   Score: 3.78 / 5.0   (ambient, chill)
     - mood match: chill (+2.0)
     - energy 0.28 vs target 0.40 (+1.32)
     - acoustic sound (+0.46)

4. Focus Flow - LoRoom
   Score: 2.89 / 5.0   (lofi, focused)
     - energy 0.40 vs target 0.40 (+1.50)
     - genre match: lofi (+1.0)
     - acoustic sound (+0.39)

5. Coffee Shop Stories - Slow Stereo
   Score: 1.90 / 5.0   (jazz, relaxed)
     - energy 0.37 vs target 0.40 (+1.46)
     - acoustic sound (+0.45)
```

#### Deep Intense Rock

```
================================================================
Profile: Deep Intense Rock
  mood=intense  genre=rock  energy=0.9  likes_acoustic=False
================================================================
1. Storm Runner - Voltline
   Score: 4.93 / 5.0   (rock, intense)
     - mood match: intense (+2.0)
     - energy 0.91 vs target 0.90 (+1.48)
     - genre match: rock (+1.0)
     - electronic sound (+0.45)

2. Gym Hero - Max Pulse
   Score: 3.93 / 5.0   (pop, intense)
     - mood match: intense (+2.0)
     - energy 0.93 vs target 0.90 (+1.46)
     - electronic sound (+0.47)

3. Pulse Horizon - Kilowatt Kid
   Score: 1.91 / 5.0   (edm, euphoric)
     - energy 0.95 vs target 0.90 (+1.43)
     - electronic sound (+0.48)

4. Iron Verdict - Ashfall
   Score: 1.88 / 5.0   (metal, angry)
     - energy 0.97 vs target 0.90 (+1.40)
     - electronic sound (+0.48)

5. Sunrise City - Neon Echo
   Score: 1.79 / 5.0   (pop, happy)
     - energy 0.82 vs target 0.90 (+1.38)
     - electronic sound (+0.41)
```

#### Sad but Hyped

```
================================================================
Profile: Sad but Hyped
  mood=sad  genre=blues  energy=0.9  likes_acoustic=False
================================================================
1. Empty Platform - Grey Harbor
   Score: 3.73 / 5.0   (blues, sad)
     - mood match: sad (+2.0)
     - energy 0.30 vs target 0.90 (+0.60)
     - genre match: blues (+1.0)
     - electronic sound (+0.13)

2. Storm Runner - Voltline
   Score: 1.93 / 5.0   (rock, intense)
     - energy 0.91 vs target 0.90 (+1.48)
     - electronic sound (+0.45)

3. Gym Hero - Max Pulse
   Score: 1.93 / 5.0   (pop, intense)
     - energy 0.93 vs target 0.90 (+1.46)
     - electronic sound (+0.47)

4. Pulse Horizon - Kilowatt Kid
   Score: 1.91 / 5.0   (edm, euphoric)
     - energy 0.95 vs target 0.90 (+1.43)
     - electronic sound (+0.48)

5. Iron Verdict - Ashfall
   Score: 1.88 / 5.0   (metal, angry)
     - energy 0.97 vs target 0.90 (+1.40)
     - electronic sound (+0.48)
```

#### Acoustic Headbanger

```
================================================================
Profile: Acoustic Headbanger
  mood=angry  genre=metal  energy=0.95  likes_acoustic=True
================================================================
1. Iron Verdict - Ashfall
   Score: 4.48 / 5.0   (metal, angry)
     - mood match: angry (+2.0)
     - energy 0.97 vs target 0.95 (+1.47)
     - genre match: metal (+1.0)
     - acoustic sound (+0.01)

2. Pulse Horizon - Kilowatt Kid
   Score: 1.52 / 5.0   (edm, euphoric)
     - energy 0.95 vs target 0.95 (+1.50)
     - acoustic sound (+0.02)

3. Gym Hero - Max Pulse
   Score: 1.50 / 5.0   (pop, intense)
     - energy 0.93 vs target 0.95 (+1.47)
     - acoustic sound (+0.03)

4. Storm Runner - Voltline
   Score: 1.49 / 5.0   (rock, intense)
     - energy 0.91 vs target 0.95 (+1.44)
     - acoustic sound (+0.05)

5. Sunrise City - Neon Echo
   Score: 1.40 / 5.0   (pop, happy)
     - energy 0.82 vs target 0.95 (+1.30)
     - acoustic sound (+0.09)
```

#### Unknown Tastes

```
================================================================
Profile: Unknown Tastes
  mood=dreamy  genre=k-pop  energy=0.5  likes_acoustic=False
================================================================
1. Silk Afterglow - Nia Solace
   Score: 1.72 / 5.0   (r&b, romantic)
     - energy 0.55 vs target 0.50 (+1.42)
     - electronic sound (+0.30)

2. Dusty Porch Light - Willow Creek Band
   Score: 1.65 / 5.0   (country, nostalgic)
     - energy 0.52 vs target 0.50 (+1.47)
     - electronic sound (+0.18)

3. Island Breeze Delay - Coral Sound System
   Score: 1.62 / 5.0   (reggae, uplifting)
     - energy 0.60 vs target 0.50 (+1.35)
     - electronic sound (+0.28)

4. Midnight Coding - LoRoom
   Score: 1.52 / 5.0   (lofi, chill)
     - energy 0.42 vs target 0.50 (+1.38)
     - electronic sound (+0.15)

5. Concrete Crown - Blockwise
   Score: 1.52 / 5.0   (hip-hop, confident)
     - energy 0.78 vs target 0.50 (+1.08)
     - electronic sound (+0.44)
```

#### Sloppy Input

```
================================================================
Profile: Sloppy Input
  mood=Chill  genre=Lofi  energy=1.5  likes_acoustic=True
================================================================
1. Iron Verdict - Ashfall
   Score: 0.72 / 5.0   (metal, angry)
     - energy 0.97 vs target 1.50 (+0.70)
     - acoustic sound (+0.01)

2. Pulse Horizon - Kilowatt Kid
   Score: 0.69 / 5.0   (edm, euphoric)
     - energy 0.95 vs target 1.50 (+0.67)
     - acoustic sound (+0.02)

3. Gym Hero - Max Pulse
   Score: 0.67 / 5.0   (pop, intense)
     - energy 0.93 vs target 1.50 (+0.65)
     - acoustic sound (+0.03)

4. Storm Runner - Voltline
   Score: 0.67 / 5.0   (rock, intense)
     - energy 0.91 vs target 1.50 (+0.61)
     - acoustic sound (+0.05)

5. Sunrise City - Neon Echo
   Score: 0.57 / 5.0   (pop, happy)
     - energy 0.82 vs target 1.50 (+0.48)
     - acoustic sound (+0.09)
```

---

## 8. Future Work  

1. **Give partial credit for similar moods and genres.** Group moods into families (calm = chill, relaxed, focused; dark = sad, melancholic, moody; intense = intense, angry, euphoric), and treat "indie pop" as close to "pop." That would fix Iron Verdict ranking below a pop song for rock fans, and relaxed jazz missing out for chill fans.
2. **Clean up and check user input.** Lowercase labels before comparing and keep energy between 0 and 1, so "Chill" works and an energy of 1.5 can't create negative scores.
3. **Be honest when nothing fits, and add variety.** Show a "no strong matches" note when the top score is low (around 2 out of 5 or below), and limit each artist to one spot in the top 5. Allowing several moods per user and adding a "happy vs sad" (valence) preference would also help listeners with mixed or rarer tastes.

---

## 9. Personal Reflection  

**Biggest learning moment.** Honestly, it was the "Sloppy Input" test. I basically made a copy of my own chill lofi profile, but typed it sloppily: "Chill" with a capital C, and energy set to 1.5. It gave me metal and EDM. No error, no warning, just a confident list of completely wrong songs. That one stuck with me, because it made me realize these systems don't break loudly. They just quietly give you bad answers. The weight experiment was a smaller "oh" moment. I was sure doubling the energy weight would shake things up, and it barely changed anything. That's when it clicked that my problem wasn't the numbers, it was the labels.

**Using AI (and catching it).** AI was really useful for the stuff I didn't want to spend forever on, like reading the CSV, making the terminal output look clean, and coming up with weird test profiles I wouldn't have thought of. But I learned pretty fast not to just trust it. It got the number of moods in my dataset wrong twice, and I only noticed because I ran the count myself. The starter tests were also passing the whole time, even though they were testing placeholder code, so a green checkmark didn't mean much. The decision I'm proudest of came from me, not the AI: the suggested weights put genre first, and I flipped it to mood first because that's just how I pick music. I don't open my app thinking "I want jazz." I think "I need something chill."

**What surprised me.** How little it takes for something to *feel* smart. It's literally adding up a few points and sorting a list. But when my Chill Lofi list came back with my two lofi songs and then an ambient track I never asked for, it kind of felt like it got me. The reasons printed under each song made it feel even more legit, but they also gave the trick away. Gym Hero kept showing up everywhere, not because the system loves it, but because there are only five high-energy songs in the whole catalog. It made me look at my real Spotify recommendations a little differently.

**What I'd try next.** I'd start by fixing what bugged me most: giving partial credit for moods and genres that are close (angry metal should count for an intense rock fan), and cleaning up input so a capital letter can't wreck everything. After that, I'd let people pick more than one mood, since nobody's taste is just one word. And I'd really like to try a tiny version of collaborative filtering with a few fake users' likes and skips, just to see how "people like you also liked this" compares to what I built.
