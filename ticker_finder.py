import difflib


def similarity_score(s1, s2):
    # Function to calculate the similarity between strings s1 and s2
    s1_lower = s1.lower()
    s2_lower = s2.lower()
    matcher = difflib.SequenceMatcher(None, s1_lower, s2_lower)
    return matcher.ratio()


def find_similar_ticker(commodity_selected, data_tickers):
    commodity_selected = (
        commodity_selected.split(" - ")[0]
        .replace("index", "")
        .replace("futures", "")
        .replace("-", " ")
        .replace("ultra","")
    )
    commodity_selected = " ".join(commodity_selected.split()[:3])
    best_match = None
    best_score = 0.0

    for value in data_tickers.values():
        score = similarity_score(commodity_selected, value)
        if score > best_score:
            best_match = value
            best_score = score

    if best_match is not None and best_score >= 0.6:
        return data_tickers.inverse[best_match]
    else:
        # Try to reverse the word order in the user's query and compare again
        reversed_commodity_selected = " ".join(reversed(commodity_selected.split()))
        reversed_score = (
            similarity_score(reversed_commodity_selected, best_match)
            if best_match
            else 0.0
        )
        if reversed_score >= 0.6:
            tk = data_tickers.inverse[best_match]
            print("Ticker found ", tk)
            return tk
        else:
            print("No matching ticker found.")
            return None
