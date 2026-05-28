"""MLA 9th edition citation format."""

from .base import BaseFormat


class MLAFormat(BaseFormat):
    """MLA 9th edition citation style."""

    @property
    def name(self):
        return "MLA 9th"

    @property
    def ordering(self):
        return "alphabetical"

    @property
    def in_text_style(self):
        return "author_page"

    @property
    def min_refs(self):
        return 10

    def authors_to_str(self, authors, max_authors=2):
        """Format: Last, First, and First Last."""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors[:max_authors]):
            result.append(self._format_mla_name(author.strip()))
        if len(authors) > max_authors:
            if len(result) == 1:
                result.append("et al.")
            else:
                result.append("et al.")
        if len(result) == 1:
            return result[0]
        elif len(result) == 2:
            return f"{result[0]}, and {result[1]}"
        return ", ".join(result[:-1]) + f", and {result[-1]}"

    def _format_mla_name(self, name):
        """Convert 'Yun Wang' to 'Wang, Yun'."""
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first = ' '.join(parts[:-1])
            return f"{last}, {first}"
        return name

    def format_journal(self, ref):
        """Last, First. "Title." Journal, vol. X, no. Y, Year, pp. Z."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        year = ref.get('year', '')
        pages = ref.get('pages', '')
        doi = ref.get('doi', '')

        parts = [f'{authors}. "{title}."']
        if journal:
            parts[-1] += f" *{journal}*"
        if volume:
            parts[-1] += f", vol. {volume}"
        if issue:
            parts[-1] += f", no. {issue}"
        if year:
            parts[-1] += f", {year}"
        if pages:
            parts[-1] += f", pp. {pages}"
        parts[-1] += "."
        if doi:
            parts[-1] += f" doi:{doi}"
        return " ".join(parts)

    def format_conference(self, ref):
        """Last, First. "Title." Conference, Year, Place."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        year = ref.get('year', '')
        place = ref.get('place', '')

        parts = [f'{authors}. "{title}."']
        if proceedings:
            parts[-1] += f" *{proceedings}*"
        if year:
            parts[-1] += f", {year}"
        if place:
            parts[-1] += f", {place}"
        parts[-1] += "."
        return " ".join(parts)

    def format_book(self, ref):
        """Last, First. *Title*. Publisher, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [f'{authors}. *{title}*.']
        if publisher:
            parts[-1] += f" {publisher}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_dissertation(self, ref):
        """Last, First. "Title." Diss. Institution, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        institution = ref.get('institution', ref.get('publisher', ''))
        year = ref.get('year', '')

        parts = [f'{authors}. "{title}."']
        parts[-1] += " Diss."
        if institution:
            parts[-1] += f" {institution}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_patent(self, ref):
        return self.format_journal(ref)

    def format_standard(self, ref):
        return self.format_book(ref)

    def format_electronic(self, ref):
        """Last, First. "Title." Website, Publisher, Date, URL."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        site = ref.get('site', ref.get('publisher', ''))
        date = ref.get('year', '')
        url = ref.get('url', '')

        parts = []
        if authors:
            parts.append(f'{authors}. "{title}."')
        else:
            parts.append(f'"{title}."')
        if site:
            parts[-1] += f" *{site}*"
        if date:
            parts[-1] += f", {date}"
        if url:
            parts[-1] += f", {url}"
        parts[-1] += "."
        return " ".join(parts)

    def format_other(self, ref):
        return self.format_journal(ref)
