"""
med.papers - Scientific Paper Generator for MOISSCode
Generates publishing-ready LaTeX/PDF papers in journal-specific formats.
Supports IEEE, medRxiv, bioRxiv, JAMA, Nature, Lancet, PLOS ONE, and generic.
"""

import os
import subprocess
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# ── Data Models ────────────────────────────────────────

@dataclass
class PaperSection:
    """A section or subsection of a paper."""
    heading: str
    content: str
    subsections: List['PaperSection'] = field(default_factory=list)


@dataclass
class PaperData:
    """Complete paper data structure."""
    title: str
    authors: List[Dict[str, str]]   # [{name, affiliation, email}]
    abstract: str
    keywords: List[str] = field(default_factory=list)
    sections: List[PaperSection] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)
    figures: List[Dict[str, str]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    format: str = "generic"
    date: str = field(default_factory=lambda: datetime.date.today().isoformat())
    doi: str = ""
    acknowledgments: str = ""
    funding: str = ""
    conflicts: str = "The authors declare no competing interests."


# ── LaTeX Templates ────────────────────────────────────

TEMPLATES: Dict[str, Dict[str, str]] = {

    # ─── IEEE Conference / Transactions ─────────────────
    "ieee": {
        "name": "IEEE Conference / Transactions",
        "documentclass": r"\documentclass[conference]{IEEEtran}",
        "preamble": r"""
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{cite}
\usepackage{hyperref}
""",
        "title_block": r"""
\title{%(title)s}
%(author_block)s
\maketitle
""",
        "author_format": "ieee",
        "abstract_env": "abstract",
        "bib_style": "IEEEtran",
        "columns": 2,
    },

    # ─── medRxiv Preprint ───────────────────────────────
    "medrxiv": {
        "name": "medRxiv Preprint",
        "documentclass": r"\documentclass[11pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{lineno}
\linenumbers
\usepackage{setspace}
\doublespacing
""",
        "title_block": r"""
\title{\textbf{%(title)s}}
%(author_block)s
\date{%(date)s}
\maketitle
""",
        "author_format": "standard",
        "abstract_env": "abstract",
        "bib_style": "unsrtnat",
        "columns": 1,
        "header_note": r"\noindent\textbf{NOTE: This preprint reports new research that has not been certified by peer review and should not be used to guide clinical practice.}\\\vspace{1em}",
    },

    # ─── bioRxiv Preprint ───────────────────────────────
    "biorxiv": {
        "name": "bioRxiv Preprint",
        "documentclass": r"\documentclass[11pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{lineno}
\linenumbers
\usepackage{setspace}
\onehalfspacing
""",
        "title_block": r"""
\title{\textbf{%(title)s}}
%(author_block)s
\date{%(date)s}
\maketitle
""",
        "author_format": "standard",
        "abstract_env": "abstract",
        "bib_style": "unsrtnat",
        "columns": 1,
    },

    # ─── JAMA ───────────────────────────────────────────
    "jama": {
        "name": "JAMA (Journal of the American Medical Association)",
        "documentclass": r"\documentclass[twocolumn,10pt]{article}",
        "preamble": r"""
\usepackage[margin=0.75in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{times}
\usepackage{enumitem}
""",
        "title_block": r"""
\twocolumn[
  \begin{@twocolumnfalse}
  \begin{center}
  {\Large\bfseries %(title)s}\\[1em]
  %(author_block)s
  \end{center}
  \vspace{1em}
  \end{@twocolumnfalse}
]
""",
        "author_format": "inline",
        "abstract_env": "abstract",
        "bib_style": "unsrtnat",
        "columns": 2,
        "structured_abstract": True,
    },

    # ─── Nature ─────────────────────────────────────────
    "nature": {
        "name": "Nature",
        "documentclass": r"\documentclass[10pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
""",
        "title_block": r"""
\title{\textbf{%(title)s}}
%(author_block)s
\date{}
\maketitle
""",
        "author_format": "standard",
        "abstract_env": "abstract",
        "bib_style": "naturemag",
        "columns": 1,
    },

    # ─── Lancet ─────────────────────────────────────────
    "lancet": {
        "name": "The Lancet",
        "documentclass": r"\documentclass[12pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{setspace}
\doublespacing
""",
        "title_block": r"""
\title{\textbf{%(title)s}}
%(author_block)s
\date{}
\maketitle
""",
        "author_format": "standard",
        "abstract_env": "abstract",
        "bib_style": "unsrtnat",
        "columns": 1,
        "structured_abstract": True,
    },

    # ─── PLOS ONE ───────────────────────────────────────
    "plos": {
        "name": "PLOS ONE",
        "documentclass": r"\documentclass[10pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{setspace}
\onehalfspacing
\usepackage{xcolor}
""",
        "title_block": r"""
\title{\textbf{%(title)s}}
%(author_block)s
\date{}
\maketitle
""",
        "author_format": "numbered",
        "abstract_env": "abstract",
        "bib_style": "plos2015",
        "columns": 1,
    },

    # ─── Generic Academic ───────────────────────────────
    "generic": {
        "name": "Generic Academic Paper",
        "documentclass": r"\documentclass[12pt]{article}",
        "preamble": r"""
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{setspace}
\onehalfspacing
""",
        "title_block": r"""
\title{%(title)s}
%(author_block)s
\date{%(date)s}
\maketitle
""",
        "author_format": "standard",
        "abstract_env": "abstract",
        "bib_style": "unsrt",
        "columns": 1,
    },
}


# ── Engine ──────────────────────────────────────────────

class PapersEngine:
    """Scientific paper generator for MOISSCode."""

    SUPPORTED_FORMATS = list(TEMPLATES.keys())

    def __init__(self):
        self.templates = TEMPLATES

    # ── Public API ──────────────────────────────────────

    def list_formats(self) -> dict:
        """List all supported journal/preprint formats."""
        return {
            'type': 'PAPERS_FORMATS',
            'formats': {k: v['name'] for k, v in self.templates.items()},
            'count': len(self.templates),
        }

    def get_template(self, fmt: str) -> dict:
        """Return template metadata for a given format."""
        fmt = fmt.lower().strip()
        tmpl = self.templates.get(fmt)
        if not tmpl:
            return {'type': 'PAPERS', 'error': f'Unknown format: {fmt}. Use list_formats() to see options.'}
        return {
            'type': 'PAPERS_TEMPLATE',
            'format': fmt,
            'name': tmpl['name'],
            'documentclass': tmpl['documentclass'],
            'columns': tmpl.get('columns', 1),
            'structured_abstract': tmpl.get('structured_abstract', False),
        }

    def generate(self, title: str, authors: list, abstract: str,
                 sections: list = None, keywords: list = None,
                 references: list = None, figures: list = None,
                 tables: list = None, fmt: str = "generic",
                 acknowledgments: str = "", funding: str = "",
                 conflicts: str = "", doi: str = "") -> dict:
        """
        Generate a structured paper from provided content.

        Args:
            title: Paper title
            authors: List of dicts with 'name', 'affiliation', 'email'
            abstract: Abstract text
            sections: List of dicts with 'heading', 'content', and optional 'subsections'
            keywords: List of keyword strings
            references: List of dicts with 'key', 'type', 'authors', 'title', 'journal', 'year', 'volume', 'pages', 'doi'
            figures: List of dicts with 'caption', 'path', 'label'
            tables: List of dicts with 'caption', 'headers', 'rows', 'label'
            fmt: Output format (ieee, medrxiv, biorxiv, jama, nature, lancet, plos, generic)
            acknowledgments: Acknowledgments text
            funding: Funding statement
            conflicts: Conflicts of interest statement
            doi: DOI if available

        Returns:
            dict with paper data and LaTeX source
        """
        fmt = fmt.lower().strip()
        if fmt not in self.templates:
            return {'type': 'PAPERS', 'error': f'Unknown format: {fmt}'}

        # Normalize authors
        norm_authors = []
        for a in (authors or []):
            if isinstance(a, str):
                norm_authors.append({'name': a, 'affiliation': '', 'email': ''})
            else:
                norm_authors.append({
                    'name': a.get('name', 'Unknown'),
                    'affiliation': a.get('affiliation', ''),
                    'email': a.get('email', ''),
                })

        # Normalize sections
        norm_sections = self._normalize_sections(sections or [])

        paper = PaperData(
            title=title,
            authors=norm_authors,
            abstract=abstract,
            keywords=keywords or [],
            sections=norm_sections,
            references=references or [],
            figures=figures or [],
            tables=tables or [],
            format=fmt,
            acknowledgments=acknowledgments,
            funding=funding,
            conflicts=conflicts or "The authors declare no competing interests.",
            doi=doi,
        )

        latex_source = self.to_latex(paper)

        return {
            'type': 'PAPERS_GENERATED',
            'title': title,
            'format': fmt,
            'format_name': self.templates[fmt]['name'],
            'authors': [a['name'] for a in norm_authors],
            'section_count': len(norm_sections),
            'reference_count': len(paper.references),
            'figure_count': len(paper.figures),
            'table_count': len(paper.tables),
            'latex_source': latex_source,
            'latex_lines': latex_source.count('\n') + 1,
        }

    def to_latex(self, paper: PaperData) -> str:
        """Render a PaperData object into a complete LaTeX document string."""
        tmpl = self.templates.get(paper.format, self.templates['generic'])
        lines = []

        # Document class
        lines.append(tmpl['documentclass'])

        # Preamble
        lines.append(tmpl['preamble'].strip())

        # Begin document
        lines.append(r"\begin{document}")
        lines.append("")

        # Header note (e.g., medRxiv disclaimer)
        if 'header_note' in tmpl:
            lines.append(tmpl['header_note'])
            lines.append("")

        # Title & authors
        author_block = self._format_authors(paper.authors, tmpl.get('author_format', 'standard'))
        title_block = tmpl['title_block'] % {
            'title': self._escape_latex(paper.title),
            'author_block': author_block,
            'date': paper.date,
        }
        lines.append(title_block.strip())
        lines.append("")

        # Abstract
        abstract_env = tmpl.get('abstract_env', 'abstract')
        lines.append(f"\\begin{{{abstract_env}}}")
        lines.append(paper.abstract)
        lines.append(f"\\end{{{abstract_env}}}")
        lines.append("")

        # Keywords
        if paper.keywords:
            lines.append(r"\noindent\textbf{Keywords:} " + ", ".join(paper.keywords))
            lines.append("")

        # Sections
        for section in paper.sections:
            lines.extend(self._render_section(section, level=0))
            lines.append("")

        # Figures
        for fig in paper.figures:
            lines.extend(self._render_figure(fig))
            lines.append("")

        # Tables
        for tbl in paper.tables:
            lines.extend(self._render_table(tbl))
            lines.append("")

        # Acknowledgments
        if paper.acknowledgments:
            lines.append(r"\section*{Acknowledgments}")
            lines.append(paper.acknowledgments)
            lines.append("")

        # Funding
        if paper.funding:
            lines.append(r"\section*{Funding}")
            lines.append(paper.funding)
            lines.append("")

        # Conflicts of interest
        if paper.conflicts:
            lines.append(r"\section*{Declaration of Interests}")
            lines.append(paper.conflicts)
            lines.append("")

        # References
        if paper.references:
            lines.extend(self._render_references(paper.references, tmpl.get('bib_style', 'unsrt')))
            lines.append("")

        lines.append(r"\end{document}")

        return "\n".join(lines)

    def to_pdf(self, paper_data: dict, output_path: str) -> dict:
        """
        Compile LaTeX source to PDF.
        Requires pdflatex installed on the system.

        Args:
            paper_data: Output from generate() containing 'latex_source'
            output_path: Path for the output PDF file

        Returns:
            dict with compilation status
        """
        if 'latex_source' not in paper_data:
            return {'type': 'PAPERS', 'error': 'No latex_source in paper_data. Run generate() first.'}

        latex_source = paper_data['latex_source']
        output_dir = os.path.dirname(os.path.abspath(output_path))
        base_name = os.path.splitext(os.path.basename(output_path))[0]

        os.makedirs(output_dir, exist_ok=True)

        tex_path = os.path.join(output_dir, f"{base_name}.tex")
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_source)

        try:
            # Run pdflatex twice for cross-references
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode',
                     '-output-directory', output_dir, tex_path],
                    capture_output=True, text=True, timeout=60
                )

            pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
            if os.path.exists(pdf_path):
                return {
                    'type': 'PAPERS_PDF',
                    'status': 'SUCCESS',
                    'pdf_path': pdf_path,
                    'tex_path': tex_path,
                    'size_bytes': os.path.getsize(pdf_path),
                }
            else:
                return {
                    'type': 'PAPERS_PDF',
                    'status': 'FAILED',
                    'tex_path': tex_path,
                    'error': 'PDF not generated. Check LaTeX log.',
                    'log': result.stdout[-2000:] if result.stdout else '',
                }

        except FileNotFoundError:
            return {
                'type': 'PAPERS_PDF',
                'status': 'FAILED',
                'tex_path': tex_path,
                'error': 'pdflatex not found. Install a TeX distribution (TeX Live, MiKTeX) to compile PDFs.',
            }
        except subprocess.TimeoutExpired:
            return {
                'type': 'PAPERS_PDF',
                'status': 'FAILED',
                'tex_path': tex_path,
                'error': 'pdflatex compilation timed out (60s limit).',
            }

    def add_references(self, paper_data: dict, refs: list) -> dict:
        """Attach additional references to an existing paper."""
        if 'latex_source' not in paper_data:
            return {'type': 'PAPERS', 'error': 'No latex_source in paper_data.'}

        bib_entries = self._render_references(refs, 'unsrt')
        latex = paper_data['latex_source']

        # Insert before \end{document}
        end_doc = r"\end{document}"
        if end_doc in latex:
            latex = latex.replace(end_doc, "\n".join(bib_entries) + "\n\n" + end_doc)

        paper_data['latex_source'] = latex
        paper_data['reference_count'] = paper_data.get('reference_count', 0) + len(refs)
        return paper_data

    def add_figure(self, paper_data: dict, caption: str, path: str, label: str = "") -> dict:
        """Insert a figure into an existing paper."""
        if 'latex_source' not in paper_data:
            return {'type': 'PAPERS', 'error': 'No latex_source in paper_data.'}

        fig = {'caption': caption, 'path': path, 'label': label or f"fig:{len(paper_data.get('figures', []))+1}"}
        fig_lines = self._render_figure(fig)
        latex = paper_data['latex_source']

        end_doc = r"\end{document}"
        if end_doc in latex:
            latex = latex.replace(end_doc, "\n".join(fig_lines) + "\n\n" + end_doc)

        paper_data['latex_source'] = latex
        paper_data['figure_count'] = paper_data.get('figure_count', 0) + 1
        return paper_data

    def add_table(self, paper_data: dict, caption: str,
                  headers: list, rows: list, label: str = "") -> dict:
        """Insert a table into an existing paper."""
        if 'latex_source' not in paper_data:
            return {'type': 'PAPERS', 'error': 'No latex_source in paper_data.'}

        tbl = {'caption': caption, 'headers': headers, 'rows': rows,
               'label': label or f"tab:{paper_data.get('table_count', 0)+1}"}
        tbl_lines = self._render_table(tbl)
        latex = paper_data['latex_source']

        end_doc = r"\end{document}"
        if end_doc in latex:
            latex = latex.replace(end_doc, "\n".join(tbl_lines) + "\n\n" + end_doc)

        paper_data['latex_source'] = latex
        paper_data['table_count'] = paper_data.get('table_count', 0) + 1
        return paper_data

    # ── Private Helpers ─────────────────────────────────

    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escape special LaTeX characters in plain text."""
        special = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
                   '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
                   '^': r'\textasciicircum{}'}
        for char, replacement in special.items():
            text = text.replace(char, replacement)
        return text

    def _normalize_sections(self, sections: list) -> List[PaperSection]:
        """Convert dicts to PaperSection objects recursively."""
        result = []
        for s in sections:
            if isinstance(s, PaperSection):
                result.append(s)
            elif isinstance(s, dict):
                subsections = self._normalize_sections(s.get('subsections', []))
                result.append(PaperSection(
                    heading=s.get('heading', 'Untitled'),
                    content=s.get('content', ''),
                    subsections=subsections,
                ))
        return result

    def _format_authors(self, authors: List[Dict], style: str) -> str:
        """Format author block based on journal style."""
        if not authors:
            return ""

        if style == "ieee":
            blocks = []
            for a in authors:
                block = r"\IEEEauthorblockN{%s}" % a['name']
                if a.get('affiliation'):
                    block += "\n" + r"\IEEEauthorblockA{%s}" % a['affiliation']
                    if a.get('email'):
                        block += r"\\ " + a['email']
                blocks.append(block)
            return r"\author{" + r" \and ".join(blocks) + "}"

        elif style == "numbered":
            # PLOS-style: numbered affiliations
            affiliations = []
            aff_map = {}
            author_strs = []
            for a in authors:
                aff = a.get('affiliation', '')
                if aff and aff not in aff_map:
                    aff_map[aff] = len(aff_map) + 1
                    affiliations.append(aff)
                sup = f"$^{{{aff_map.get(aff, '')}}}$" if aff else ""
                author_strs.append(f"{a['name']}{sup}")

            author_line = r"\author{" + ", ".join(author_strs) + "}"
            aff_lines = []
            for i, aff in enumerate(affiliations, 1):
                aff_lines.append(f"$^{{{i}}}$ {aff}")
            return author_line + "\n" + r"\date{" + r" \\ ".join(aff_lines) + "}"

        elif style == "inline":
            # JAMA-style: inline
            names = ", ".join(a['name'] for a in authors)
            affs = "; ".join(set(a['affiliation'] for a in authors if a.get('affiliation')))
            return f"{names}\\\\[0.5em]\\textit{{{affs}}}"

        else:
            # Standard: \author{Name1 \and Name2}
            entries = []
            for a in authors:
                entry = a['name']
                if a.get('affiliation'):
                    entry += r" \\ \textit{" + a['affiliation'] + "}"
                if a.get('email'):
                    entry += r" \\ \texttt{" + a['email'] + "}"
                entries.append(entry)
            return r"\author{" + r" \and ".join(entries) + "}"

    def _render_section(self, section: PaperSection, level: int = 0) -> list:
        """Render a section and its subsections to LaTeX lines."""
        lines = []
        cmds = [r"\section", r"\subsection", r"\subsubsection"]
        cmd = cmds[min(level, len(cmds) - 1)]

        lines.append(f"{cmd}{{{section.heading}}}")
        if section.content:
            lines.append(section.content)

        for sub in section.subsections:
            lines.extend(self._render_section(sub, level + 1))

        return lines

    def _render_figure(self, fig: dict) -> list:
        """Render a figure environment."""
        label = fig.get('label', '')
        lines = [
            r"\begin{figure}[htbp]",
            r"    \centering",
            r"    \includegraphics[width=0.9\linewidth]{%s}" % fig.get('path', 'figure.png'),
            r"    \caption{%s}" % fig.get('caption', ''),
        ]
        if label:
            lines.append(r"    \label{%s}" % label)
        lines.append(r"\end{figure}")
        return lines

    def _render_table(self, tbl: dict) -> list:
        """Render a table environment."""
        headers = tbl.get('headers', [])
        rows = tbl.get('rows', [])
        label = tbl.get('label', '')
        col_spec = "|".join(["c"] * len(headers)) if headers else "c"

        lines = [
            r"\begin{table}[htbp]",
            r"    \centering",
            r"    \caption{%s}" % tbl.get('caption', ''),
        ]
        if label:
            lines.append(r"    \label{%s}" % label)
        lines.append(r"    \begin{tabular}{|%s|}" % col_spec)
        lines.append(r"        \hline")

        if headers:
            lines.append(r"        " + " & ".join(str(h) for h in headers) + r" \\")
            lines.append(r"        \hline")

        for row in rows:
            lines.append(r"        " + " & ".join(str(c) for c in row) + r" \\")

        lines.append(r"        \hline")
        lines.append(r"    \end{tabular}")
        lines.append(r"\end{table}")
        return lines

    def _render_references(self, refs: list, bib_style: str) -> list:
        """Render references as a thebibliography environment (no external .bib needed)."""
        if not refs:
            return []

        lines = [r"\begin{thebibliography}{%d}" % len(refs)]

        for ref in refs:
            key = ref.get('key', f"ref{refs.index(ref)+1}")
            authors = ref.get('authors', 'Unknown')
            title = ref.get('title', 'Untitled')
            journal = ref.get('journal', '')
            year = ref.get('year', '')
            volume = ref.get('volume', '')
            pages = ref.get('pages', '')
            doi = ref.get('doi', '')

            entry = f"\\bibitem{{{key}}} {authors}. "
            entry += f"``{title}.'' "
            if journal:
                entry += f"\\textit{{{journal}}}"
                if volume:
                    entry += f", {volume}"
                if pages:
                    entry += f", pp. {pages}"
            if year:
                entry += f", {year}."
            if doi:
                entry += f" doi: {doi}"

            lines.append(entry)

        lines.append(r"\end{thebibliography}")
        return lines
