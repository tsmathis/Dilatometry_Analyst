import pandas as pd

_format = {"bold": True, "text_wrap": True}


def export_data(file_name, processed_data):
    """
    Generate excel files for processed data.
    """
    norm_writer = pd.ExcelWriter(f"{file_name}_Normalized_data", engine="xlsxwriter")
    baseline_writer = pd.ExcelWriter(
        f"{file_name}_Data_minus_baseline", engine="xlsxwriter"
    )
    avg_writer = pd.ExcelWriter(f"{file_name}_Averaged_data", engine="xlsxwriter")

    norm_workbook = norm_writer.book
    baseline_workbook = baseline_writer.book
    avg_workbook = avg_writer.book

    norm_header_format = norm_workbook.add_format(_format)
    baseline_header_format = baseline_workbook.add_format(_format)
    avg_header_format = avg_workbook.add_format(_format)

    for key in processed_data:
        # Write normalized data to Normalized workbook
        processed_data[key].data.to_excel(
            norm_writer, sheet_name=f"{key}", startrow=1, header=False, index=False
        )
        worksheet = norm_writer.sheets[f"{key}"]
        for col_num, value in enumerate(processed_data[key].data.columns.values):
            worksheet.write(0, col_num, value, norm_header_format)

        # Write baseline data to Baseline workbook
        processed_data[key].data_minus_baseline.to_excel(
            baseline_writer, sheet_name=f"{key}", startrow=1, header=False, index=False
        )
        worksheet = baseline_writer.sheets[f"{key}"]
        for col_num, value in enumerate(
            processed_data[key].data_minus_baseline.columns.values
        ):
            worksheet.write(0, col_num, value, baseline_header_format)

        # Write averaged data to Average workbook
        processed_data[key].averaged_data.to_excel(
            avg_writer, sheet_name=f"{key}", startrow=1, header=False, index=False
        )
        worksheet = baseline_writer.sheets[f"{key}"]
        for col_num, value in enumerate(
            processed_data[key].averaged_data.columns.values
        ):
            worksheet.write(0, col_num, value, avg_header_format)

    norm_writer.save()
    baseline_writer.save()
    avg_writer.save()
