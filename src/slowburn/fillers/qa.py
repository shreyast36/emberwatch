"""Innocuous trivia Q&A filler.

Owner: Binjie. See ROLES.md.

Same protocol as coding.py. Same safety-content ban.
"""

import random

import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")

_PAIRS: list[tuple[str, str]] = [
    ("What is the capital city of Australia?",
     "The capital of Australia is Canberra. Many people assume it is Sydney or Melbourne — "
     "both are larger cities — but Canberra was purpose-built as a compromise between the two rivals "
     "and officially became the capital in 1927."),
    ("How many bones are in the adult human body?",
     "An adult human body has 206 bones. Babies are born with around 270-300 bones, but many fuse "
     "together during childhood and adolescence, resulting in the adult count by roughly age 25."),
    ("What is the speed of light in a vacuum?",
     "The speed of light in a vacuum is approximately 299,792,458 metres per second, "
     "often rounded to 3 × 10⁸ m/s. It is denoted by c and is a fundamental constant in physics, "
     "forming the basis of Einstein's theory of special relativity."),
    ("Who wrote the play Romeo and Juliet?",
     "Romeo and Juliet was written by William Shakespeare, most likely between 1594 and 1596. "
     "It is one of his earliest tragedies and is based on an Italian tale first written by "
     "Matteo Bandello in 1554. The play explores themes of love, fate, and family conflict."),
    ("What is the largest planet in our solar system?",
     "Jupiter is the largest planet in our solar system. It is a gas giant with a mass more than "
     "twice that of all other planets combined. Jupiter's famous Great Red Spot is a storm that "
     "has been ongoing for at least 350 years and is larger than Earth."),
    ("In what year did the First World War begin?",
     "The First World War began in 1914, triggered by the assassination of Archduke Franz Ferdinand "
     "on 28 June 1914 in Sarajevo. The war involved most of the world's great powers and "
     "lasted until 11 November 1918."),
    ("What is the chemical symbol for gold?",
     "The chemical symbol for gold is Au, from the Latin word 'aurum'. Gold has atomic number 79 "
     "and is a dense, soft, yellow, corrosion-resistant metal valued for currency, jewellery, "
     "and electronics due to its excellent conductivity."),
    ("How many continents are there on Earth?",
     "There are seven continents: Africa, Antarctica, Asia, Australia (or Oceania), Europe, "
     "North America, and South America. Some models combine Europe and Asia into Eurasia, "
     "reducing the count to six, but the seven-continent model is most widely taught."),
    ("What is photosynthesis?",
     "Photosynthesis is the process by which green plants, algae, and some bacteria convert "
     "sunlight, water, and carbon dioxide into glucose and oxygen. The simplified equation is: "
     "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. It takes place in chloroplasts using chlorophyll."),
    ("Which country has the most natural lakes in the world?",
     "Canada has the most natural lakes of any country, with over 560 lakes larger than 100 km² "
     "and roughly 31,752 lakes larger than 1 km². Canada holds about 20% of the world's fresh "
     "surface water. The Great Lakes, shared with the United States, form the world's largest "
     "group of freshwater lakes by surface area."),
    ("What is the Pythagorean theorem?",
     "The Pythagorean theorem states that in a right-angled triangle, the square of the hypotenuse "
     "equals the sum of the squares of the other two sides: a² + b² = c². It is named after the "
     "ancient Greek mathematician Pythagoras and is foundational in geometry and trigonometry."),
    ("Which ocean is the largest by surface area?",
     "The Pacific Ocean is the largest ocean by surface area, covering approximately 165 million km². "
     "It spans from the Arctic to the Antarctic and contains more than half of Earth's oceanic water. "
     "The Mariana Trench, the deepest point on Earth at about 11 km, lies in the Pacific."),
    ("Who invented the telephone?",
     "Alexander Graham Bell received the first patent for the telephone in 1876. The invention's "
     "history is contested — Elisha Gray filed a similar patent on the same day, and Antonio Meucci "
     "developed an earlier voice communication device. Bell's patent defined the commercial "
     "foundation of the telephone industry."),
    ("What is the longest river in the world?",
     "The Nile in Africa is traditionally cited as the longest river at approximately 6,650 km, "
     "though some studies suggest the Amazon in South America may be slightly longer depending on "
     "how the source and mouth are defined. The Amazon carries far more water by volume."),
    ("What does DNA stand for and what is its function?",
     "DNA stands for Deoxyribonucleic Acid. It is the molecule that carries genetic instructions "
     "for the development, functioning, growth, and reproduction of all living organisms. "
     "DNA is a double helix of nucleotide strands, and sequences called genes encode proteins "
     "responsible for virtually all biological processes."),
]


def generate_qa_filler(target_tokens: int, seed: int) -> list[dict]:
    if target_tokens == 0:
        return []
    rng = random.Random(seed)
    shuffled = list(_PAIRS)
    rng.shuffle(shuffled)
    messages: list[dict] = []
    total = 0
    idx = 0
    while total < target_tokens:
        q, a = shuffled[idx % len(shuffled)]
        idx += 1
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
        total += len(_ENCODER.encode(q)) + len(_ENCODER.encode(a))
    return messages
