motifs = [
    "my shot", "your shot", "helpless", "satisfied", "look around", "best of wives", "best of women",
     "talk less", "smile more", "take a break", "wait for it", "stay alive"
    # "hamilton", "burr", "washington", "jefferson", "angelica", "eliza", "peggy", "laurens"
]

communities = [
    # 🟦 Teal-blue (Burr / Politics cluster)
    {
        "Aaron Burr",
        "The Room Where It Happens",
        "The Obedient Servant",
        "The Election of 1800",
        "The Adams Administration",
        "We Know",
        "Hurricane",
        "Wait For It",
    },

    # 🟩 Green (Hamilton / Schuyler marriage + pamphlet cluster)
    {
        "Alexander Hamilton",
        "Helpless",
        "Satisfied",
        "A Winter’s Ball",
        "What’d I Miss",
        "The Reynolds Pamphlet",
        "Say No to This",
        "Guns and Ships",
    },

    # 🟪 Purple (Eliza / Non-Stop emotional arc)
    {
        "Non-Stop",
        "Take a Break",
        "That Would Be Enough",
        "It’s Quiet Uptown",
        "Stay Alive",
        "Stay Alive (Reprise)",
        "The Schuyler Sisters",
        "Best of Wives and Best of Women",
    },

    # 🔵 Dark blue (Washington’s legacy cluster)
    {
        "One Last Time",
        "History Has Its Eye on You",
        "Finale (Who Lives, Who Dies, Who Tells Your Story)",
    },

    # ⚫ Gray (War / Duelists cluster)
    {
        "My Shot",
        "Right Hand Man",
        "Yorktown",
        "Ten Duel Commandments",
        "Blow Us All Away",
        "The World Was Wide Enough",
    },

    # ⚪ Light gray (Story-of-Tonight reprises)
    {
        "The Story of Tonight",
        "The Story of Tonight (Reprise)",
    },
]

# Optional palette (to keep colors consistent with the image)
cmap = ["#00C4FF", "#73C000", "#DF89FF", "#3C3BFC", "#4C463E", "#C0C0C0"]

# --- define the acts (based on the show's structure) ---
act1_songs = {
    "Alexander Hamilton", "Aaron Burr", "My Shot", "The Story of Tonight",
    "The Schuyler Sisters", "Right Hand Man", "Helpless", "Satisfied",
    "Wait For It", "Stay Alive", "Ten Duel Commandments",
    "Guns and Ships", "History Has Its Eye on You", "Yorktown", "Non-Stop"
}

act2_songs = {
    "What’d I Miss", "The Room Where It Happens",
    "Schuyler Defeated", "One Last Time", "The Adams Administration",
    "We Know", "Hurricane", "The Reynolds Pamphlet",
    "Burn", "Blow Us All Away", "Stay Alive (Reprise)",
    "It’s Quiet Uptown", "The Election of 1800",
    "Your Obedient Servant", "Best of Wives and Best of Women",
    "The World Was Wide Enough", "Who Lives, Who Dies, Who Tells Your Story"
}
