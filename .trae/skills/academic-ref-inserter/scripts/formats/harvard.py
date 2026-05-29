"""Harvard citation format (author-date, alphabetical)."""

from .base import BaseFormat


class HarvardFormat(BaseFormat):
    """Harvard citation style."""

    @property
    def name(self):
        return "Harvard"

    @property
    def ordering(self):
        return "alphabetical"

    @property
    def in_text_style(self):
        return "author_year"

    @property
    def min_refs(self):
        return 10

    def authors_to_str(self, authors, max_authors=3):
        """Format: Last, I. and Last, I."""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors[:max_authors]):
            result.append(self._format_harvard_name(author.strip()))
        if len(authors) > max_authors:
            result.append("et al.")
        if len(result) == 1:
            return result[0]
        elif len(result) == 2:
            return f"{result[0]} and {result[1]}"
        return ", ".join(result[:-1]) + f" and {result[-1]}"

    def _format_harvard_name(self, name):
        """Convert 'Yun Wang' to 'Wang, Y.'"""
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = '.'.join(p[0].upper() for p in parts[:-1]) + '.'
            return f"{last}, {initials}"
        return name

    def format_journal(self, ref):
        """Last, I. (Year) 'Title', Journal, Vol(Issue), pp. X-Y. doi:XX"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        doi = ref.get('doi', '')

        parts = [f"{authors} ({year})"]
        parts[-1] += f" '{title}',"
        if journal:
            parts[-1] += f" *{journal}*"
        if volume:
            parts[-1] += f", {volume}"
            if issue:
                parts[-1] += f"({issue})"
        if pages:
            parts[-1] += f", pp. {pages}"
        parts[-1] += "."
        if doi:
            parts[-1] += f" doi:{doi}"
        return " ".join(parts)

    def format_conference(self, ref):
        """Last, I. (Year) 'Title', in Proceedings, Place, pp. X-Y."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        year = ref.get('year', '')
        pages = ref.get('pages', '')
        place = ref.get('place', '')

        parts = [f"{authors} ({year})"]
        parts[-1] += f" '{title}',"
        if proceedings:
            parts[-1] += f" in {proceedings}"
        if place:
            parts[-1] += f", {place}"
        if pages:
            parts[-1] += f", pp. {pages}"
        parts[-1] += "."
        return " ".join(parts)

    def format_book(self, ref):
        """Last, I. (Year) *Title*. Edition. Place: Publisher."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        edition = ref.get('edition', '')
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [f"{authors} ({year})"]
        parts[-1] += f" *{title}*."
        if edition:
            parts[-1] += f" {edition} edn."
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f" {': '.join(loc)}"
        parts[-1] += "."
        return " ".join(parts)

    def format_dissertation(self, ref):
        """Last, I. (Year) 'Title'. PhD thesis. Institution."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        institution = ref.get('institution', ref.get('publisher', ''))
        year = ref.get('year', '')

        parts = [f"{authors} ({year})"]
        parts[-1] += f" '{title}'."
        parts[-1] += " PhD thesis."
        if institution:
            parts[-1] += f" {institution}"
        parts[-1] += "."
        return " ".join(parts)

    def format_patent(self, ref):
        return self.format_journal(ref)

    def format_standard(self, ref):
        return self.format_book(ref)

    def format_electronic(self, ref):
        """Author (Year) *Title*. Available at: URL (Accessed: Date)."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        year = ref.get('year', '')
        url = ref.get('url', '')

        parts = [f"{authors} ({year})"]
        parts[-1] += f" *{title}*."
        if url:
            parts[-1] += f" Available at: {url}"
        parts[-1] += "."
        return " ".join(parts)

    def format_other(self, ref):
        return self.format_journal(ref)
