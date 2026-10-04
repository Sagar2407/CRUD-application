"""Shot list for "Stop Comparing! What Is Meant for You Is Still Growing" (5-minute cut).

Each shot is one Seedance 2.0 clip with at most one line of voice-over.
  id       file name for every artifact of the shot
  section  chapter the shot belongs to (see SECTIONS)
  vo       narration as it should appear in captions ("" for a music-only shot)
  tts      optional pronunciation override sent to the voice engine (Sanskrit lines)
  krishna  True: reference-to-video with the Krishna reference frame, keeps his look consistent
  hold     seconds of picture for a shot with no narration
  thumb    True: frame used for out/thumbnail_base.jpg
  prompt   what Seedance should draw; STYLE is appended to every prompt

Keep each vo line to about 22 words so voice plus breathing room fits in a 15-second clip.
"""

TITLE = "Stop Comparing! What Is Meant for You Is Still Growing \U0001F33E | Shri Krishna Motivation"

STYLE = (
    "Cinematic devotional film look, rich painterly colours inspired by Indian miniature art, "
    "warm golden light, soft volumetric haze, gentle film grain, shallow depth of field, "
    "slow graceful motion. No on-screen text, no captions, no logos, no watermark."
)

KRISHNA = (
    "Lord Krishna: a youthful, serene deity with luminous blue skin, a gentle knowing smile, "
    "a peacock feather in a golden crown, a yellow silk pitambar, pearl and tulsi garlands, "
    "and a bamboo bansuri flute"
)

# Prefixed to every krishna=True prompt; @Image1 is the reference frame made by the `ref` step.
KRISHNA_LOCK = (
    "@Image1 is Lord Krishna. Keep his face, blue skin, golden crown, peacock feather and yellow "
    "clothing exactly as in @Image1. His lips stay closed; he does not speak."
)

REF_PROMPT = (
    f"Head-and-shoulders portrait of {KRISHNA}. He faces the camera, centred, calm, lips closed, "
    "a golden wheat field at dusk softly blurred behind him. Almost perfectly still; only the "
    "peacock feather stirs in a light breeze."
)

SECTIONS = {
    "hook": "Why you feel left behind",
    "seen": "Krishna has seen your struggle",
    "path": "Walk your own path (Gita 3.35)",
    "story": "The wheat and the mango tree",
    "changes": "Four changes to make today",
    "blessing": "Your time is coming",
}

SHOTS = [
    # ---- Hook ----
    dict(id="a01", section="hook", krishna=True,
         vo="You give everything you have. Every single day.",
         prompt="Extreme close-up of @Image1's eyes slowly opening, calm and compassionate, a golden "
                "wheat field at dusk softly blurred behind him. Very slow push-in."),
    dict(id="a02", section="hook",
         vo="And still, you watch others move ahead. Their jobs. Their homes. Their happiness. "
            "While you stand in the same place.",
         prompt="Night rooftop in an Indian city. A young man in a plain white kurta, seen only from "
                "behind, sits alone on the ledge with his phone glowing in his hand, city lights "
                "stretching to the horizon. The camera drifts slowly closer over his shoulder; the "
                "phone screen stays a soft blur."),
    dict(id="a03", section="hook", krishna=True,
         vo="Stop for a moment, my child. This message did not reach you by accident.",
         prompt="Medium shot of @Image1 standing in a golden wheat field at dusk. He turns his head "
                "toward the camera with a gentle smile as wind ripples through the wheat and his "
                "garland. Slow arc around him."),
    dict(id="a04", section="hook", krishna=True,
         vo="Before it ends, you will know why your harvest hasn't come yet.",
         prompt="Close-up of @Image1's blue hand lifting a single golden stalk of wheat against the "
                "setting sun, the grains glowing; focus then shifts to his serene face behind it. "
                "Slow push-in."),

    # ---- Validation ----
    dict(id="b01", section="seen", krishna=True,
         vo="I have seen you. I have seen the nights you lay awake, measuring your life against theirs.",
         prompt="@Image1 sits beneath a kadamba tree on the bank of the Yamuna at moonrise, fireflies "
                "drifting, the river glowing silver. Slow dolly-in."),
    dict(id="b02", section="seen",
         vo="I have seen you work when no one was watching, and try again when no one believed in you.",
         prompt="A young man in a plain white kurta, seen only from behind, studies at a small wooden "
                "desk by the light of a single oil lamp late at night, books stacked high, his shadow "
                "on a bare wall. Static camera; the flame flickers."),
    dict(id="b03", section="seen", krishna=True,
         vo="Listen to me. You are not weak. You are not behind. You are tired, because you've been "
            "running someone else's race.",
         prompt="Close-up of @Image1 looking directly into the camera with deep compassion, soft "
                "moonlight on his face, the peacock feather catching the light. Very slow push-in."),

    # ---- Reframe: Gita 3.35 ----
    dict(id="c01", section="path", vo="", hold=4.5,
         prompt="Wide aerial shot of the battlefield of Kurukshetra at dawn: two vast armies face each "
                "other in drifting mist, and a single golden chariot drawn by white horses stands "
                "between them. Slow descending camera."),
    dict(id="c02", section="path", krishna=True,
         vo="On the battlefield of Kurukshetra, I told Arjuna: shreyan sva-dharmo vigunah, "
            "para-dharmat sv-anushthitat.",
         tts="On the battlefield of Kurukshetra, I told Arjuna... Shreyaan swa-dharmo vigunah... "
             "para-dharmaat swa-nushthitaat.",
         prompt="@Image1 stands on a golden chariot at Kurukshetra and turns toward the archer Arjuna "
                "beside him, raising his right hand in blessing, saffron banners rippling in the wind. "
                "Low angle, slow push-in."),
    dict(id="c03", section="path", krishna=True,
         vo="It is better to walk your own path, even imperfectly, than to walk another's path perfectly.",
         prompt="@Image1 walks alone along a narrow dirt path through green fields at sunrise, faint "
                "golden footprints glowing behind him. Side tracking shot."),
    dict(id="c04", section="path",
         vo="The moment you compare, you judge your roots against their fruit. And whoever keeps "
            "looking sideways forgets to look ahead.",
         prompt="A young man in a plain white kurta, seen only from behind, stands at a crossroads at "
                "sunrise with his head turned toward a crowd hurrying down another road. The camera "
                "cranes slowly up to reveal his own long, empty road stretching ahead into golden light."),

    # ---- Parable ----
    dict(id="d01", section="story",
         vo="Let me tell you a story. In a village near Vrindavan, a farmer planted two things on the same day.",
         prompt="At dawn in a village near Vrindavan, an old Indian farmer with a white turban, grey "
                "beard and kind, weathered face kneels in fresh red earth, pressing seeds into the soil "
                "with his hands. Mud houses and a temple spire in the distance. Slow push-in."),
    dict(id="d02", section="story",
         vo="In one field, wheat. In the other, a single mango seed.",
         prompt="Top-down shot of two neighbouring plots of red earth: on the left, neat freshly sown "
                "furrows; on the right, one small mound with a single large mango seed resting beside "
                "it. The camera slowly descends."),
    dict(id="d03", section="story",
         vo="Within weeks, the wheat came up green. Within months, it turned gold, and the whole "
            "village came to admire it.",
         prompt="Time-lapse of a wheat field sprouting green and ripening into waving gold under racing "
                "clouds; villagers in colourful clothes gather at its edge, smiling and pointing. Wide shot."),
    dict(id="d04", section="story",
         vo="And the mango? A thin little stem. A few leaves. Nothing more.",
         prompt="Macro close-up of a tiny mango sapling with only three leaves in dry red earth; a "
                "single drop of water falls onto a leaf. Shallow depth of field, golden wheat blurred behind."),
    dict(id="d05", section="story",
         vo="His son asked, \"Father, why do you still water that useless plant?\" The farmer only "
            "smiled and said: keep watering.",
         prompt="The old farmer with the white turban and grey beard stands beside the tiny mango "
                "sapling with his ten-year-old son in a faded blue kurta. The boy gestures at the "
                "sapling, puzzled; the farmer smiles and gently pours water onto it from a brass pot. "
                "Medium shot, warm morning light. No one speaks."),
    dict(id="d06", section="story",
         vo="Season after season, the wheat was sown and cut, again and again.",
         prompt="Locked-off wide time-lapse across the seasons: the wheat field is harvested, sown and "
                "ripens again through monsoon rain, winter mist and summer sun, while the mango "
                "sapling slowly thickens into a young tree."),
    dict(id="d07", section="story",
         vo="Then came the summer the rains failed. The wheat withered. The fields cracked.",
         prompt="Drought: a withered brown wheat field, the earth split into deep cracks under a harsh "
                "white sun, heat haze shimmering. Slow pan across the cracked ground."),
    dict(id="d08", section="story",
         vo="But the mango tree, whose roots had grown deep while no one watched, stood tall and "
            "heavy with fruit, for forty years.",
         prompt="The camera rises slowly from cracked earth up the thick trunk of a tall, lush mango "
                "tree heavy with ripe golden mangoes, green and alive in the middle of the drought, "
                "sunbeams streaming through its leaves."),
    dict(id="d09", section="story", krishna=True, thumb=True,
         vo="Some people are wheat. They rise fast. Some people are mango trees. They spend years "
            "building roots that nobody sees.",
         prompt="@Image1 stands in the shade of the great mango tree with one hand resting on its "
                "trunk, looking toward the camera with a knowing smile. Slow arc around him."),
    dict(id="d10", section="story", krishna=True,
         vo="Would you call the mango tree a failure because the wheat was harvested first? Then why "
            "do you call yourself one?",
         prompt="Close-up of @Image1, eyes soft and full of love, holding a ripe mango in his open palm "
                "as golden light flickers through the leaves. Very slow push-in."),

    # ---- Four changes ----
    dict(id="e01", section="changes", krishna=True,
         vo="Starting today, first: guard your eyes. When comparison begins, put the phone down and "
            "ask: did I water my own field today?",
         prompt="A young man in a plain white kurta, seen only from behind, places his glowing phone "
                "face-down on a wooden table beside an oil lamp. @Image1 stands softly out of focus "
                "in the background, watching with approval."),
    dict(id="e02", section="changes",
         vo="Second: measure yourself only against who you were yesterday. One step better is a victory.",
         prompt="A young man in a plain white kurta, seen only from behind, climbs the worn stone steps "
                "of a river ghat at sunrise, one steady step at a time, the river glittering below. "
                "Tracking shot from behind."),
    dict(id="e03", section="changes",
         vo="Third: keep watering, even when nothing shows. On this path, no effort is ever lost.",
         prompt="Macro shot of weathered hands pouring water from a brass pot onto the base of a young "
                "plant at dawn. The water soaks in, and the camera tilts down through a cutaway of the "
                "soil to reveal glowing roots spreading outward."),
    dict(id="e04", section="changes", krishna=True,
         vo="And fourth: offer the fruit to me. Do your work fully, and let go of when the harvest comes.",
         prompt="@Image1 receives a woven basket of ripe mangoes offered by unseen hands and smiles; a "
                "soft golden glow surrounds him as marigold petals drift through the air. Medium shot, "
                "slow push-in."),
    dict(id="e05", section="changes", krishna=True,
         vo="Karmany evadhikaras te, ma phaleshu kadachana. Your right is to the work, never to its fruit.",
         tts="Karmanye vaadhikaaraste... maa phaleshu kadaachana. Your right is to the work... never "
             "to its fruit.",
         prompt="@Image1 plays his bansuri flute on a riverbank at golden hour, eyes closed in peace, "
                "cows grazing behind him. Slow arc."),

    # ---- Blessing and call to action ----
    dict(id="f01", section="blessing", krishna=True,
         vo="My child, what is meant for you is not late. It is growing. When your season comes, no "
            "one can stop it.",
         prompt="Sunrise over a vast golden wheat field: @Image1 walks beside a young man in a plain "
                "white kurta, both seen from behind, and rests a hand on his shoulder. Wide tracking "
                "shot from behind them."),
    dict(id="f02", section="blessing", krishna=True,
         vo="Stop looking at their field. Look at yours.",
         prompt="Close-up of @Image1 smiling warmly in rich sunrise light, a soft lens flare and "
                "drifting petals, the wheat field glowing behind him. Slow push-in."),
    dict(id="f03", section="blessing", krishna=True,
         vo="I was there when you sowed the seed. And I will be there on the day of your harvest.",
         prompt="@Image1's blue hand gently presses a seed into dark soil; in the same shot a golden "
                "wheat field and a fruiting mango tree rise around it in a smooth time-lapse. Low "
                "angle, slow push-in."),
    dict(id="f04", section="blessing", krishna=True,
         vo="Rise now. Your time is coming.",
         prompt="Wide shot: on a hilltop above the fields, @Image1 raises his bansuri to his lips as "
                "the sun rises fully behind him, rays spreading across the sky. Slow crane up."),
    dict(id="f05", section="blessing",
         vo="If this reached your heart, write Jai Shri Krishna in the comments. And send it to one "
            "person who needs it today.",
         prompt="A single oil lamp glowing on a temple step at dusk beside a peacock feather and a ripe "
                "mango, marigold petals scattered around. Very slow push-in. Calm final image."),
]

DESCRIPTION = """Do you feel everyone around you is moving ahead while you stay stuck in the same place? Do you keep comparing your life to theirs and feel left behind?

In this message, Shri Krishna explains why what is meant for you is not late. It is still growing. Through the Bhagavad Gita and the story of the wheat and the mango tree, learn to stop comparing and trust your own path.

{chapters}

If this reached your heart, write "Jai Shri Krishna" in the comments.

#ShriKrishna #KrishnaMotivation #BhagavadGita
"""

TAGS = [
    "shri krishna motivation", "krishna vani", "bhagavad gita motivation", "stop comparing yourself",
    "krishna motivational speech", "geeta gyan", "krishna updesh", "krishna arjun",
    "your time will come", "spiritual motivation",
]
