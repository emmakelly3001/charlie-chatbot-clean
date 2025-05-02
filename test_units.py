from Charlie import find_best_match, wrap_with_friendly_tone, random_fallback, qa_dict, question_embeddings

def test_find_best_match():
    q1 = "Where do I access my exam timetable"
    result = find_best_match(q1, qa_dict, question_embeddings)
    print(f"Match for '{q1}': {result}")

def test_wrap_with_friendly_tone():
    raw = "You can log into Moodle at moodle.ncirl.ie using your student number."
    wrapped = wrap_with_friendly_tone(raw)
    print("Wrapped Answer:\n", wrapped)

def test_random_fallback():
    fallback = random_fallback()
    print("Fallback Message:\n", fallback)

if __name__ == "__main__":
    test_find_best_match()
    test_wrap_with_friendly_tone()
    test_random_fallback()
