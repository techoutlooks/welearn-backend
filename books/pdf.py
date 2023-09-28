import fitz

from books.settings import get_setting


def make_pdf_preview(in_path, filename, page_ranges):
    """
    Generate a new PDF file from given page ranges and save it on disk
    Nota: fitz aka. PyMuPDF works with zero-indexed pages.

    :param in_path: full path of input file to create a preview from
    :param filename: name of output file without path.
    :param page_ranges: page numbers as a string eg. '1, 3-5, 20-22' to create preview from.
    :return: tuple of output file path (if succedeed) and page list `make_pdf_preview`
            attempted to create the preview from.
    """

    out_path = None
    pages = parse_pages(page_ranges)

    try:
        input = fitz.open(in_path)
        output = fitz.open()
        pages, _ = get_valid_preview_pages(pages, input.pageCount)
        for p in pages:
            output.insertPDF(input, from_page=p-1, to_page=p-1)

    except Exception as e:
        raise PreviewPDFException(filename, e)

    else:
        out_path = f"{get_setting('TMP_DIR')}/{filename}"
        output.save(out_path)

    return out_path, pages


def make_preview_filename(filename):
    """
    File name including extension, but no path, eg. `deeplearningbook-preview.pdf`
    :param filename: name of original file a preview is being generated from.
    """
    filename_, ext = filename.rsplit('.', 1)
    return f"{filename_}-{get_setting('PREVIEW_PREFIX')}.{ext}"


def parse_pages(s: str):
    """
    Create from a string, a list of unique page numbers (int)
    arranged in the natural order of a book pages.
    eg. '1, 3-5, 20-22' => [1,3,4,5, 10, 20,21,22]
    """
    pages = []
    for s_pp in s.split(','):
        pp = [int(p) for p in s_pp.strip().split('-')]
        if len(pp) == 1:
            pp = pp + pp
        pp[1] += 1
        pages.extend([p for p in range(*pp)])

    return sorted(set(pages))


def pdf_info(path):

    pdf = fitz.open(path)
    return dict(
        page_count=pdf.pageCount,
        metadata=pdf.metadata,
        toc=pdf.toc
    )


def get_valid_preview_pages(preview_pages, page_count):
    """
    Get valid list of pages for previewing,
    extracted from preview_pages upper bounded by page_max.
    :param preview_pages: list of pages to create preview from (sorted in natural order)
    :param page_max: page count of original (full pages) PDF doc
    """
    closest_value = min(preview_pages, key=lambda x: abs(x - page_count))
    valid_pages = preview_pages[:preview_pages.index(closest_value) + 1]

    # some logging # TODO: some syslogging
    preview_last_page = preview_pages[len(preview_pages) - 1]
    valid = preview_last_page > page_count
    if valid:
        msg = (
            f'Preview page number {preview_last_page} of {page_count} pages out of bounds. ' 
            f'Truncating to pages {",".join([str(p) for p in valid_pages])}.'
        )
        print(msg)

    return valid_pages, valid


class PreviewPDFException(Exception):
    """
    https://stackoverflow.com/q/6180185
    """
    def __init__(self, filename, error, *args,  **kwargs):
        self.filename = filename
        self.error = error
        self.msg = f"Unrecoverable error creating PDF preview from {filename}"
        print(self.msg)
        super().__init__(*args,  **kwargs)
