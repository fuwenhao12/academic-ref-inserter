"""Base class for all citation format implementations."""

from abc import ABC, abstractmethod


class BaseFormat(ABC):
    """Abstract base class for citation formats."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable format name."""

    @property
    @abstractmethod
    def ordering(self) -> str:
        """'sequential' or 'alphabetical'."""

    @property
    @abstractmethod
    def in_text_style(self) -> str:
        """'numbered', 'author_year', or 'superscript'."""

    @property
    @abstractmethod
    def min_refs(self) -> int:
        """Minimum recommended references."""

    @abstractmethod
    def format_journal(self, ref: dict) -> str:
        """Format a journal article reference."""

    @abstractmethod
    def format_conference(self, ref: dict) -> str:
        """Format a conference paper reference."""

    @abstractmethod
    def format_book(self, ref: dict) -> str:
        """Format a book reference."""

    @abstractmethod
    def format_dissertation(self, ref: dict) -> str:
        """Format a dissertation reference."""

    @abstractmethod
    def format_patent(self, ref: dict) -> str:
        """Format a patent reference."""

    @abstractmethod
    def format_standard(self, ref: dict) -> str:
        """Format a standard reference."""

    @abstractmethod
    def format_electronic(self, ref: dict) -> str:
        """Format an electronic resource reference."""

    @abstractmethod
    def format_other(self, ref: dict) -> str:
        """Fallback for other reference types."""

    def authors_to_str(self, authors: list, max_authors: int = 3) -> str:
        """Convert author list to string. Override in subclass for style-specific formatting.
        
        Default: "Author1, Author2, Author3, et al."
        """
        if not authors:
            return ""
        result = []
        for i, author in enumerate(authors):
            if i >= max_authors:
                result.append("et al.")
                break
            result.append(author.strip())
        return ", ".join(result)

    def format(self, ref: dict) -> str:
        """Dispatch to the correct formatter based on ref type."""
        ref_type = ref.get('type', 'other').lower()
        type_map = {
            'j': self.format_journal,
            'journal': self.format_journal,
            'c': self.format_conference,
            'conference': self.format_conference,
            'm': self.format_book,
            'book': self.format_book,
            'd': self.format_dissertation,
            'dissertation': self.format_dissertation,
            'p': self.format_patent,
            'patent': self.format_patent,
            's': self.format_standard,
            'standard': self.format_standard,
            'eb/ol': self.format_electronic,
            'electronic': self.format_electronic,
            'web': self.format_electronic,
            'arxiv': self.format_journal,
        }
        formatter = type_map.get(ref_type, self.format_other)
        return formatter(ref)
