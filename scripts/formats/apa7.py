"""APA 7th edition citation format (author-year, alphabetical)."""

from .base import BaseFormat


class APA7Format(BaseFormat):
    """APA 7th edition citation style."""

    @property
    def name(self):
        return "APA 7th"

    @property
    def ordering(self):
        return "alphabetical"

    @property
    def in_text_style(self):
        return "author_year"

    @property
    def min_refs(self):
        return 15

    def authors_to_str(self, authors, max_authors=20):
        """Format: Author, A. A., & Author, B. B."""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors):
            if i >= max_authors:
                result.append("...")
                break
            result.append(self._format_apa_name(author.strip()))
        if len(result) == 1:
            return result[0]
        elif len(result) == 2:
            return f"{result[0]} & {result[1]}"
        else:
            return ", ".join(result[:-1]) + f", & {result[-1]}"

    def _format_apa_name(self, name):
        """Convert 'Yun Wang' to 'Wang, Y.'"""
        parts = name.strip().split()
        if not parts:
            return name
        if len(parts) >= 2:
            last = parts[-1]
            first_initial = parts[0][0].upper() + "."
            return f"{last}, {first_initial}"
        return parts[0]

    def format_journal(self, ref):
        """Author, A. A., & Author, B. B. (Year). Title. Journal, Vol(Issue), pages. DOI"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        doi = ref.get('doi', '')

        parts = [f"{authors} ({year}). {title}. " if year else f"{authors}. {title}. "]
        parts[-1] += journal
        vol_str = ""
        if volume:
            vol_str = volume
            if issue:
                vol_str += f"({issue})"
        if vol_str:
            parts[-1] += f", {vol_str}"
        if pages:
            parts[-1] += f", {pages}"
        parts[-1] += "."
        if doi:
            parts[-1] += f" https://doi.org/{doi}"
        return " ".join(parts)

    def format_conference(self, ref):
        """Author (Year). Title. In Proceedings (pp. X-Y). Publisher. DOI"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        year = ref.get('year', '')
        pages = ref.get('pages', '')
        publisher = ref.get('publisher', '')
        doi = ref.get('doi', '')

        parts = [f"{authors} ({year}). {title}. " if year else f"{authors}. {title}. "]
        if proceedings:
            parts[-1] += f"In *{proceedings}*"
            if pages:
                parts[-1] += f" (pp. {pages})"
            parts[-1] += "."
        if publisher:
            parts[-1] += f" {publisher}."
        if doi:
            parts[-1] += f" https://doi.org/{doi}"
        return " ".join(parts)

    def format_book(self, ref):
        """Author (Year). *Title*. Publisher. DOI"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')
        doi = ref.get('doi', '')

        parts = [f"{authors} ({year}). *{title}*. " if year else f"{authors}. *{title}*. "]
        if publisher:
            parts[-1] += f"{publisher}."
        if doi:
            parts[-1] += f" https://doi.org/{doi}"
        return " ".join(parts)

    def format_dissertation(self, ref):
        """Author (Year). *Title* [Doctoral dissertation, University]. Database."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        institution = ref.get('institution', ref.get('publisher', ''))
        year = ref.get('year', '')
        degree = ref.get('degree', 'Doctoral dissertation')

        parts = [f"{authors} ({year}). *{title}* [{degree}"]
        if institution:
            parts[-1] += f", {institution}"
        parts[-1] += "]. "
        return " ".join(parts)

    def format_patent(self, ref):
        """Inventor (Year). *Title* (Patent No. X). Source."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        patent_num = ref.get('patent_number', ref.get('number', ''))
        year = ref.get('year', '')

        parts = [f"{authors} ({year}). *{title}*"]
        if patent_num:
            parts[-1] += f" ({patent_num})"
        parts[-1] += "."
        return " ".join(parts)

    def format_standard(self, ref):
        return self.format_book(ref)

    def format_electronic(self, ref):
        """Author (Year). *Title*. Site Name. URL"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        site = ref.get('site', ref.get('publisher', ''))
        year = ref.get('year', '')
        url = ref.get('url', '')

        parts = [f"{authors} ({year}). *{title}*. " if year else f"{authors}. *{title}*. "]
        if site:
            parts[-1] += f"{site}."
        if url:
            parts[-1] += f" {url}"
        return " ".join(parts)

    def format_other(self, ref):
        return self.format_journal(ref)
