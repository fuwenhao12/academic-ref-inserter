"""GB/T 7714-2015 Chinese national standard reference format implementation."""

from .base import BaseFormat


class GBT7714Format(BaseFormat):
    """Chinese national standard GB/T 7714-2015 (顺序编码制)."""

    @property
    def name(self):
        return "GB/T 7714-2015"

    @property
    def ordering(self):
        return "sequential"

    @property
    def in_text_style(self):
        return "numbered"

    @property
    def min_refs(self):
        return 15

    def authors_to_str(self, authors, max_authors=3):
        """Format: Wang Y, Wu H, Dong J, et al."""
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors):
            if i >= max_authors:
                result.append("et al." if not self._is_chinese(author) else "等")
                break
            name = author.strip()
            if self._is_chinese_name(name):
                result.append(name)
            else:
                result.append(self._format_english_name(name))
        if len(authors) > max_authors:
            pass  # already added et al.
        return ", ".join(result)

    def _is_chinese_name(self, name):
        """Check if name contains Chinese characters."""
        return any('\u4e00' <= c <= '\u9fff' for c in name)

    def _is_chinese(self, text):
        return any('\u4e00' <= c <= '\u9fff' for c in text)

    def _format_english_name(self, name):
        """Convert 'Yun Wang' or 'Wang Y' to 'Wang Y' form."""
        parts = name.strip().split()
        if not parts:
            return name
        # Check if already in "Last F" format
        if len(parts) >= 2 and len(parts[-1]) <= 2 and parts[-1].isupper():
            return name  # Already formatted
        # Assume "First Last" -> "Last F"
        if len(parts) >= 2:
            last = parts[-1]
            first = parts[0]
            initial = first[0].upper() if first else ""
            return f"{last} {initial}"
        return name

    def _capitalize_title(self, title):
        """English: capitalize first word and proper nouns; Chinese: keep."""
        if not title:
            return title
        if self._is_chinese(title[:1]):
            return title
        return title[0].upper() + title[1:] if title else title

    def format_journal(self, ref):
        """[N] Authors. Title[J]. Journal, Year, Vol(Issue): Pages."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')

        parts = [f"{authors}. {title}[J]. {journal}"]
        if year:
            vol_issue = year
            if volume:
                vol_issue += f", {volume}"
                if issue:
                    vol_issue += f"({issue})"
            parts[-1] += f", {vol_issue}"
        if pages:
            parts[-1] += f": {pages}"
        parts[-1] += "."
        return " ".join(parts)

    def format_conference(self, ref):
        """[N] Authors. Title[C]//Proceedings. Place: Publisher, Year: Pages."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        proceedings = ref.get('proceedings', ref.get('book_title', ''))
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')
        pages = ref.get('pages', '')

        parts = [f"{authors}. {title}[C]//{proceedings}"]
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f". {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}"
        if pages:
            parts[-1] += f": {pages}"
        parts[-1] += "."
        return " ".join(parts)

    def format_book(self, ref):
        """[N] Authors. Title[M]. Place: Publisher, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [f"{authors}. {title}[M]"]
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f". {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_dissertation(self, ref):
        """[N] Authors. Title[D]. Place: Institution, Year."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        place = ref.get('place', '')
        institution = ref.get('institution', ref.get('publisher', ''))
        year = ref.get('year', '')

        parts = [f"{authors}. {title}[D]"]
        loc = []
        if place:
            loc.append(place)
        if institution:
            loc.append(institution)
        if loc:
            parts[-1] += f". {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_patent(self, ref):
        """[N] Inventors. Title[P]. Patent Number, Date."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        patent_num = ref.get('patent_number', ref.get('number', ''))
        date = ref.get('date', ref.get('year', ''))

        parts = [f"{authors}. {title}[P]"]
        if patent_num:
            parts[-1] += f": {patent_num}"
        if date:
            parts[-1] += f", {date}"
        parts[-1] += "."
        return " ".join(parts)

    def format_standard(self, ref):
        """[N] Body. Standard ID Name[S]. Place: Publisher, Year."""
        body = ref.get('authors', [''])
        body_str = body[0] if isinstance(body, list) and body else body
        std_id = ref.get('standard_id', ref.get('number', ''))
        title = ref.get('title', '')
        place = ref.get('place', '')
        publisher = ref.get('publisher', '')
        year = ref.get('year', '')

        parts = [body_str]
        if std_id:
            parts[-1] += f" {std_id}"
        if title:
            parts[-1] += f" {title}"
        parts[-1] += "[S]"
        loc = []
        if place:
            loc.append(place)
        if publisher:
            loc.append(publisher)
        if loc:
            parts[-1] += f". {', '.join(loc)}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)

    def format_electronic(self, ref):
        """[N] Authors. Title[EB/OL]. (Date)[Cited]. URL."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = self._capitalize_title(ref.get('title', ''))
        pub_date = ref.get('date', ref.get('year', ''))
        cited_date = ref.get('cited_date', '')
        url = ref.get('url', '')

        parts = [f"{authors}. {title}[EB/OL]"]
        dates = []
        if pub_date:
            dates.append(pub_date)
        if cited_date:
            dates.append(cited_date)
        if dates:
            parts[-1] += f". ({'. '.join(dates)})"
        if url:
            parts[-1] += f". {url}"
        parts[-1] += "."
        return " ".join(parts)

    def format_other(self, ref):
        """Fallback for unrecognized reference types."""
        authors = self.authors_to_str(ref.get('authors', []))
        title = ref.get('title', '')
        source = ref.get('source', ref.get('journal', ''))
        year = ref.get('year', '')
        parts = [f"{authors}. {title}"]
        if source:
            parts[-1] += f". {source}"
        if year:
            parts[-1] += f", {year}"
        parts[-1] += "."
        return " ".join(parts)
