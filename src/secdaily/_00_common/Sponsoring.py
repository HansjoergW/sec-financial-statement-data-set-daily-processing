import random

sponsor_messages = [
    "Enjoying secfsdstools? Please consider sponsoring the project!",
    "Love the tool? Your support keeps development alive – consider sponsoring!",
    "If you find this tool useful, a sponsorship would be greatly appreciated!",
    "Help us continue to improve secfsdstools by becoming a sponsor!",
    "Support open source: Sponsor secfsdstools today!",
    "Keep the updates coming – sponsor secfsdstools and fuel further development.",
    "Like what you see? Consider sponsoring to help drive innovation.",
    "Your support makes a difference. Please sponsor secfsdstools!",
    "Sponsor secfsdstools and help us build a better tool for everyone.",
    "Support innovation and open source by sponsoring secfsdstools.",
    "Your sponsorship ensures continued updates. Thank you for your support!",
    "Help us keep secfsdstools running smoothly – your sponsorship matters.",
    "If you value this tool, your sponsorship is a great way to contribute!",
    "Support the developer behind secfsdstools – consider sponsoring today.",
    "Enjoy the convenience? Sponsor secfsdstools and help us grow.",
    "Be a champion for open source – sponsor secfsdstools and support innovation."
]

def print_sponsoring_message():
    """ create sponsoring message """

    message = random.choice(sponsor_messages)

    # ANSI-Escape-Codes für Farben und Formatierungen
    reset = "\033[0m"
    bold = "\033[1m"
    yellow = "\033[33m"
    white = "\033[37m"

    # Rahmen um die Nachricht erzeugen
    border = "-" * (len(message) + 8)
    hash_border = "#" * (len(message) + 8)

    # Präsentation des Sponsor-Hinweises mit Farben und Hervorhebung
    print("\n\n")
    print(yellow + border + reset)
    print(bold + yellow + hash_border + reset)
    print("\n")
    print(bold + white + "    " + message + "    " + reset)
    print("\n")
    print(bold + white + "    https://github.com/sponsors/HansjoergW" + reset)
    print("\n")
    print(white + "    How to get in touch")
    print("    - Found a bug:             https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/issues") # pylint: disable=C0301
    print("    - Have a remark:           https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions/categories/general") # pylint: disable=C0301
    print("    - Have an idea:            https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions/categories/ideas") # pylint: disable=C0301
    print("    - Have a question:         https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions/categories/q-a") # pylint: disable=C0301
    print("    - Have something to show:  https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions/categories/show-and-tell") # pylint: disable=C0301
    print("\n")
    print("    Don't forget to star it at https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing") # pylint: disable=C0301
    print("\n")
    print("    Check out my other SEC data related project")
    print("                               https://github.com/HansjoergW/sec-fincancial-statement-data-set") # pylint: disable=C0301
    print("\n")

    print(bold + yellow + hash_border + reset)
    print(yellow + border + reset)
    print("\n\n")
