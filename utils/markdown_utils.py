from markdown2 import markdown


def render_markdown(md_text: str) -> str:
    """Convert markdown to safe HTML with basic extras."""
    if md_text is None:
        return ""
    return markdown(md_text, extras=["fenced-code-blocks", "tables", "strike", "task_list"], safe_mode="escape")
