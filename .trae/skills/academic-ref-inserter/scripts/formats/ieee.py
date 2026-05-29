"""IEEE citation format for engineering and computer science journals."""

from .base import BaseFormat


class IEEEFormat(BaseFormat):
    """IEEE citation style."""

    @property
    def name(self):
        return "IEEE"

    @property
    def ordering(self):
        return "sequential"

    @property
    def in_text_style(self):
        return "numbered"

    @property
    def min_refs(self):
        return 15

    def authors_to_str(self, authors, max_authors=6):
        """Format: A. Author, B. Author, and C. Author"""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors):
            if i >= max_authors:
                result.append("et al.")
                break
            result.append(self._format_ieee_name(author.strip()))
        if len(result) == 1:
            return result[0]
        elif len(result) == 2:
            return f"{result[0]} and {result[1]}"
        else:
            return ", ".join(result[:-1]) + f", and {result[-1]}"

    def _format_ieee_name(self, name):
        """Convert 'Yun Wang' or 'Wang Y' to 'Y. Wang'."""
        parts = name.strip().split()
        if not parts:
            return name
        # If already in "A. Last" format (first part has a period)
        if '.' in parts[0] and len(parts) >= 2:
            return name
        # If already in "Last, A." format
        if ',' in name:
            parts2 = name.split(',')
            last = parts2[0].strip()
            first = parts2[1].strip().rstrip('.')
            return f"{first}. {last}"
        # If format is "Last I" (last word is single uppercase letter = initial)
        if len(parts) >= 2 and len(parts[-1]) == 1 and parts[-1].isalpha():
            last = parts[0]
            initial = parts[-1][0].upper() + '.'
            return f"{initial} {last}"
        # If all trailing words are short (1-2 chars), treat as "Last F M" -> "F. M. Last"
        if len(parts) >= 3 and all(len(p) <= 2 for p in parts[1:]):
            last = parts[0]
            initials = ' '.join(p[0].upper() + '.' for p in parts[1:])
            return f"{initials} {last}"
        # Assume "First Last" format
        first_initial = parts[0][0].upper() + "."
        last = parts[-1]
        return f"{first_initial} {last}"

    def format_journal(self, ref):
        """[N] A. Author, "Title," Journal, vol. X, no. Y, pp. Z, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        year = ref.get('year', '')

        parts = []
        if authors:
            parts.append(f'{authors}, "{title},"')
        else:
            parts.append(f'"{title},"')

        if journal:
            parts[-1] += f" {journal}"

        vol_str = ""
        if volume:
            vol_str = f"vol. {volume}"
        if issue:
            vol_str += f", no. {issue}"
        if vol_str:
            parts[-1] += f", {vol_str}"

        if pages:
            parts[-1] += f", pp. {pages}"
        if year:
            parts[-1] += f", {year}."
        else:
            parts[-1] += "."
        return " ".join(parts)

    def format_conference(self, ref):
        """[N] A. Author, "Title," in Proc. Conf., Year, pp. X-Y."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        year = ref.get('year', '')
        pages = ref.get('pages', '')

        parts = []
        if authors:
            parts.append(f'{authors}, "{title},"')
        else:
            parts.append(f'"{title},"')

        if proceedings:
            parts[-1] += f" in {proceedings}"
        if year:
            parts[-1] += f", {year}"
        if pages:
            parts[-1] += f", pp. {pages}"
        parts[-1] += "."
        return " ".join(parts)

    def format_book(self, ref):
        """[N] A. Author, Title, X ed. City, State: Publisher, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        edition = ref.get('edition', '')
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [f"{authors}, {title}"]
        if edition:
            parts[-1] += f", {edition} ed."
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f". {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}."
        else:
            parts[-1] += "."
        return " ".join(parts)

    def format_dissertation(self, ref):
        """[N] A. Author, "Title," Ph.D. dissertation, Dept., Univ., City, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        degree = ref.get('degree', ref.get('type', 'Ph.D. dissertation'))
        dept = ref.get('department', ref.get('institution', ''))
        university = ref.get('university', ref.get('publisher', ''))
        place = ref.get('place', '')
        year = ref.get('year', '')

        parts = [f'{authors}, "{title}," {degree}']
        loc = []
        if dept:
            loc.append(dept)
        if university:
            loc.append(university)
        if place:
            loc.append(place)
        if loc:
            parts[-1] += f", {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}."
        else:
            parts[-1] += "."
        return " ".join(parts)

    def format_patent(self, ref):
        """[N] A. Author, "Title," U.S. Patent X, Date."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        patent_num = ref.get('patent_number', ref.get('number', ''))
        date = ref.get('date', ref.get('year', ''))

        parts = [f'{authors}, "{title},"']
        if patent_num:
            parts[-1] += f" {patent_num}"
        if date:
            parts[-1] += f", {date}."
        else:
            parts[-1] += "."
        return " ".join(parts)

    def format_standard(self, ref):
        """Treat as technical report-style."""
        body = ref.get('authors', [''])
        body_str = body[0] if isinstance(body, list) and body else body
        std_id = ref.get('standard_id', ref.get('number', ''))
        title = ref.get('title', '')
        year = ref.get('year', '')

        parts = [body_str]
        if std_id:
            parts[-1] += f", {std_id}"
        if title:
            parts[-1] += f', "{title}"'
        if year:
            parts[-1] += f", {year}."
        else:
            parts[-1] += "."
        return " ".join(parts)

    def format_electronic(self, ref):
        """[N] A. Author, "Title," Year. [Online]. Available: URL"""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        year = ref.get('year', '')
        url = ref.get('url', '')

        parts = []
        if authors:
            parts.append(f'{authors}, "{title},"')
        else:
            parts.append(f'"{title},"')
        if year:
            parts[-1] += f" {year}"
        if url:
            parts[-1] += f". [Online]. Available: {url}"
        parts[-1] += "."
        return " ".join(parts)

    def format_other(self, ref):
        """Fallback using journal format."""
        return self.format_journal(ref)
