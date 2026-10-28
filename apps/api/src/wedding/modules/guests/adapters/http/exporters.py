import csv
import io
from collections.abc import Sequence
from datetime import date

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.cell.cell import Cell as SheetCell
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from wedding.modules.guests.application.export_rows import (
    HEADERS,
    Cell,
    ExportRow,
    neutralize_cell,
)

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV_MEDIA_TYPE = "text/csv; charset=utf-8"
SHEET_TITLE = "Convidados"

# Larguras por coluna, na ordem de HEADERS; Observação quebra linha.
_WIDTHS = (26, 10, 28, 16, 8, 14, 12, 24, 36, 18, 28, 48, 16, 14, 28)
_WRAPPED = {HEADERS.index("Observação"), HEADERS.index("Endereço do núcleo")}


def _csv_cell(cell: Cell) -> str:
    if cell is None:
        return ""
    if isinstance(cell, date):
        return cell.strftime("%d/%m/%Y")
    if isinstance(cell, int):
        return str(cell)
    return neutralize_cell(cell)


def write_csv(rows: Sequence[ExportRow]) -> bytes:
    """CSV em UTF-8 com BOM e separador `;`, para o Excel em português abrir cada campo na sua
    coluna e com os acentos certos (F-CNV-08, regra 3). Texto que parece fórmula leva apóstrofo."""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(HEADERS)
    for row in rows:
        writer.writerow([_csv_cell(cell) for cell in row.cells])
    return buffer.getvalue().encode("utf-8-sig")


def write_xlsx(rows: Sequence[ExportRow]) -> bytes:
    """Excel com cabeçalho em negrito e fixo, filtro, larguras e datas de verdade (F-CNV-08,
    regra 3). Todo texto é gravado como **texto**: o `openpyxl` trataria "=..." como fórmula na
    atribuição, e é o tipo forçado da célula que a impede de ser calculada."""
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = SHEET_TITLE
    sheet.append(list(HEADERS))
    for column in range(1, len(HEADERS) + 1):
        sheet.cell(row=1, column=column).font = Font(bold=True)
        sheet.column_dimensions[get_column_letter(column)].width = _WIDTHS[column - 1]
    for row_number, row in enumerate(rows, start=2):
        for column, value in enumerate(row.cells, start=1):
            cell = sheet.cell(row=row_number, column=column)
            assert isinstance(cell, SheetCell)
            if isinstance(value, str):
                cell.value = ILLEGAL_CHARACTERS_RE.sub("", value)
                cell.data_type = "s"
            elif isinstance(value, date):
                cell.value = value
                cell.number_format = "DD/MM/YYYY"
            elif value is not None:
                cell.value = value
            if (column - 1) in _WRAPPED:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{max(len(rows) + 1, 2)}"
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
