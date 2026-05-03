import difflib


def generate_diff_html(original: str, optimized: str) -> str:
    original_lines = original.splitlines(keepends=True)
    optimized_lines = optimized.splitlines(keepends=True)

    diff = difflib.HtmlDiff(wrapcolumn=80)
    return diff.make_table(
        original_lines, optimized_lines,
        fromdesc="优化前", todesc="优化后",
        context=True, numlines=3,
    )


def generate_diff_summary(original: str, optimized: str) -> dict:
    orig_words = set(original.split())
    opt_words = set(optimized.split())
    removed = orig_words - opt_words
    added = opt_words - orig_words
    return {
        "words_original": len(original.split()),
        "words_optimized": len(optimized.split()),
        "words_removed": len(removed),
        "words_added": len(added),
        "removed_terms": list(removed)[:10],
        "added_terms": list(added)[:10],
    }
