"""Chicago 17th edition citation format (notes-bibliography)."""

from .base import BaseFormat


class ChicagoFormat(BaseFormat):
    """Chicago Manual of Style 17th (notes-bibliography)."""

    @property
    def name(self):
        return "Chicago 17th"

    @property
    def ordering(self):
        return "alphabetical"

    @property
    def in_text_style(self):
        return "numbered"

    @property
    def min_refs(self):
        return 10

    def authors_to_str(self, authors, max_authors=10):
        """Format: Last, First, and First Last."""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors[:max_authors]):
            result.append(self._format_chicago_name(author.strip()))
        if len(authors) > max_authors:
            result.append("et al.")
        if len(result) == 1:
            return result[0]
        elif len(result) == 2:
            return f"{result[0]} and {result[1]}"
        return ", ".join(result[:-1]) + f", and {result[-1]}"

    def _format_chicago_name(self, name):
        """Convert 'Yun Wang' to 'Wang, Yun'."""
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first = ' '.join(parts[:-1])
            return f"{last}, {first}"
        return name

    def format_journal(self, ref):
        """Last, First. "Title." Journal Volume, no. Issue (Year): Pages."""
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
            parts[-1] += f" {volume}"
            if issue:
                parts[-1] += f", no. {issue}"
        if year:
            parts[-1] += f" ({year})"
        if pages:
            parts[-1] += f": {pages}"
        parts[-1] += "."
        if doi:
            parts[-1] += f" https://doi.org/{doi}"
        return " ".join(parts)

    def format_conference(self, ref):
        """Last, First. "Title." Paper presented at Conference, Place, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        place = ref.get('place', '')
        year = ref.get('year', '')
        pages = ref.get('pages', '')

        parts = [f'{authors}. "{title}."']
        if proceedings:
            parts[-1] += f" Paper presented at *{proceedings}*"
        if place:
            parts[-1] += f", {place}"
        if year:
            parts[-1] += f", {year}"
        if pages:
            parts[-1] += f", {pages}"
        parts[-1] += "."
        return " ".join(parts)

    def format_book(self, ref):
        """Last, First. *Title*. Place: Publisher, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [f'{authors}. *{title}*.']
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f" {'; '.join(loc)}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_dissertation(self, ref):
        """Last, First. "Title." PhD diss., University, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        institution = ref.get('institution', ref.get('publisher', ''))
        year = ref.get('year', '')

        parts = [f'{authors}. "{title}."']
        parts[-1] += " PhD diss."
        if institution:
            parts[-1] += f", {institution}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_patent(self, ref):
        return self.format_journal(ref)

    def format_standard(self, ref):
        return self.format_book(ref)

    def format_electronic(self, ref):
        """Last, First. "Title." Website. Last modified Date. URL."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        site = ref.get('site', ref.get('publisher', ''))
        year = ref.get('year', '')
        url = ref.get('url', '')

        parts = []
        if authors:
            parts.append(f'{authors}. "{title}."')
        else:
            parts.append(f'"{title}."')
        if site:
            parts[-1] += f" *{site}*"
        if year:
            parts[-1] += f", {year}"
        if url:
            parts[-1] += f". {url}"
        parts[-1] += "."
        return " ".join(parts)

    def format_other(self, ref):
        return self.format_journal(ref)
