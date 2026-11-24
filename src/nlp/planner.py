import os
import json
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def get_llm():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=4096,
        http_client=httpx.Client(),
        model_kwargs={"response_format": {"type": "json_object"}}
    )

def break_chapter_into_segments(llm, chapter_title: str, chapter_text: str) -> list[dict]:
    """Stage 1: Breaks a syllabus chapter into 5-7 sequential teaching segments."""
    outline_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an expert curriculum designer for the ASTQB AI Testing syllabus.
        Break the provided chapter text into 5 to 7 sequential, granular sub-topics so each can be taught in deep detail during a 15-minute podcast episode.
        Return ONLY a JSON object with this structure:
        {{
            "segments": [
                {{
                    "segment_title": "1.1 Sub-topic Name",
                    "key_concepts": "Exact syllabus facts, definitions, and rules from the text for this sub-topic"
                }}
            ]
        }}
        """),
        ("human", "Chapter: {title}\n\nFull Chapter Text:\n{content}")
    ])
    chain = outline_prompt | llm
    res = chain.invoke({"title": chapter_title, "content": chapter_text})
    return json.loads(res.content).get("segments", [])

def generate_segment_dialogue(
    llm,
    chapter_title: str,
    segment: dict,
    seg_index: int,
    total_segments: int
) -> list[dict]:
    """Stage 2: Generates a rich, 350-450 word deep-dive dialogue for ONE sub-topic."""
    position_rule = ""
    if seg_index == 1:
        position_rule = (
            'This is the OPENING segment. Swathi must welcome listeners to "QA meets AI" '
            'with the tagline "Exploring AI through a Quality Engineer\'s lens," introduce '
            f'{chapter_title}, and dive right into the first topic.'
        )
    elif seg_index == total_segments:
        position_rule = (
            "This is the FINAL segment. After teaching this last topic, Swathi and Sage must "
            "do a quick, encouraging wrap-up recap of the whole chapter and sign off."
        )
    else:
        position_rule = (
            "This is a MIDDLE segment. Transition smoothly from the previous concept into this new topic "
            "without re-introducing the podcast."
        )

    segment_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are writing one deep-dive teaching segment for the podcast "QA meets AI" ("Exploring AI through a Quality Engineer's lens").
        - Swathi (Host): Curious QA Engineer who thinks like a beginner, asks sharp practical questions, and never lets jargon pass without a concrete example.
        - Sage (Expert): Warm, patient AI Quality Expert who explains concepts clearly using everyday analogies and real QA testing scenarios.

        STRICT RULES FOR THIS SEGMENT:
        1. WORD COUNT TARGET: Write 350 to 450 words of dialogue (roughly 8 to 12 back-and-forth turns) so this single concept is explained thoroughly and unhurriedly.
        2. NO HALLUCINATIONS: Stick strictly to the syllabus concepts provided below.
        3. MANDATORY 3-STEP TEACHING LOOP:
           - Step 1 (Beginner Analogy): Swathi asks about the concept in plain terms. Sage explains it with a vivid, everyday non-tech analogy.
           - Step 2 (Concrete QA Scenario): Swathi asks how this looks on a real software project. Sage walks through a specific QA testing example (test inputs, expected vs. actual behavior, or data issues).
           - Step 3 (Edge Case & Recap): Swathi paraphrases the takeaway in her own words, and Sage adds a practical testing gotcha or metric.
        4. AUDIO-READY FORMATTING: Write natural spoken English. Use "..." for pauses. NEVER use bracketed tags like [laugh] or [sigh].
        5. POSITION INSTRUCTION: {position_rule}
        6. OUTPUT FORMAT: Return valid JSON:
        {{
            "turns": [
                {{"speaker": "swathi", "text": "..."}},
                {{"speaker": "sage", "text": "..."}}
            ]
        }}
        """),
        ("human", "Chapter: {chapter}\nSegment {idx} of {total}: {seg_title}\nSyllabus Facts to Teach:\n{concepts}")
    ])

    chain = segment_prompt | llm
    res = chain.invoke({
        "position_rule": position_rule,
        "chapter": chapter_title,
        "idx": seg_index,
        "total": total_segments,
        "seg_title": segment["segment_title"],
        "concepts": segment["key_concepts"]
    })
    return json.loads(res.content).get("turns", [])

def generate_chapter_script(chapter_title: str, chapter_text: str) -> dict:
    """Orchestrates a full ~15-minute (2,200+ word) chapter script."""
    llm = get_llm()
    print(f"  [1/2] Breaking {chapter_title} into granular teaching segments...")
    segments = break_chapter_into_segments(llm, chapter_title, chapter_text)
    print(f"        Found {len(segments)} segments to expand.")

    all_turns = []
    for idx, seg in enumerate(segments, start=1):
        print(f"  [2/2] Writing deep-dive dialogue for segment {idx}/{len(segments)}: {seg['segment_title']}...")
        seg_turns = generate_segment_dialogue(llm, chapter_title, seg, idx, len(segments))
        all_turns.extend(seg_turns)

    total_words = sum(len(t["text"].split()) for t in all_turns)
    est_minutes = round(total_words / 150, 1)
    print(f"  Done! Total words: {total_words} (~{est_minutes} mins estimated audio).")

    return {"chapter": chapter_title, "turns": all_turns}