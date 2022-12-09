import pandas as pd

_format = {"bold": True, "text_wrap": True}
invalid_chars = ["/", "\\", "[", "]", "*", ":", "?"]


def export_data(norm_file, baseline_file, average_file, processed_data):
    """
    Generate excel files for processed data.
    """
    norm_writer = pd.ExcelWriter(f"{norm_file}.xlsx", engine="xlsxwriter")
    baseline_writer = pd.ExcelWriter(f"{baseline_file}.xlsx", engine="xlsxwriter")
    avg_writer = pd.ExcelWriter(f"{average_file}.xlsx", engine="xlsxwriter")

    norm_workbook = norm_writer.book
    baseline_workbook = baseline_writer.book
    avg_workbook = avg_writer.book

    norm_header_format = norm_workbook.add_format(_format)
    baseline_header_format = baseline_workbook.add_format(_format)
    avg_header_format = avg_workbook.add_format(_format)

    for key in processed_data:
        sheet_name = "".join(ch for ch in key if ch not in invalid_chars)
        # Write normalized data to Normalized workbook
        processed_data[key].data.to_excel(
            norm_writer, sheet_name=sheet_name, startrow=1, header=False, index=False
        )
        norm_worksheet = norm_writer.sheets[sheet_name]
        for col_num, value in enumerate(processed_data[key].data.columns.values):
            norm_worksheet.write(0, col_num, value, norm_header_format)

        # Write baseline data to Baseline workbook
        processed_data[key].data_minus_baseline.to_excel(
            baseline_writer,
            sheet_name=sheet_name,
            startrow=1,
            header=False,
            index=False,
        )
        baseline_worksheet = baseline_writer.sheets[sheet_name]
        for col_num, value in enumerate(
            processed_data[key].data_minus_baseline.columns.values
        ):
            baseline_worksheet.write(0, col_num, value, baseline_header_format)

        # Write averaged data to Average workbook
        processed_data[key].averaged_data.to_excel(
            avg_writer, sheet_name=sheet_name, startrow=1, header=False, index=False
        )
        avg_worksheet = avg_writer.sheets[sheet_name]
        for col_num, value in enumerate(
            processed_data[key].averaged_data.columns.values
        ):
            avg_worksheet.write(0, col_num, value, avg_header_format)

    norm_writer.close()
    baseline_writer.close()
    avg_writer.close()
