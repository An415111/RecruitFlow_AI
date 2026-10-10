import re

def render_html_table(rows):
    if not rows:
        return ""
    
    headers = rows[0]
    data_rows = rows[1:]
    
    thead = "".join(f"<th style='padding: 12px; background-color: #0f172a; color: #ffffff; font-weight: bold; text-align: left; font-size: 13px; border: 1px solid #cbd5e1;'>{h}</th>" for h in headers)
    
    tbody_rows = []
    for idx, r in enumerate(data_rows):
        # Alternating row colors
        bg_color = "#f8fafc" if idx % 2 == 0 else "#ffffff"
        row_html = "".join(f"<td style='padding: 10px 12px; border: 1px solid #cbd5e1; font-size: 13px; color: #334155;'>{cell}</td>" for cell in r)
        tbody_rows.append(f"<tr style='background-color: {bg_color};'>{row_html}</tr>")
        
    tbody = "\n".join(tbody_rows)
    
    return f"""
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <thead>
            <tr>{thead}</tr>
        </thead>
        <tbody>
            {tbody}
        </tbody>
    </table>
    """

def generate_hotlist_html(markdown_body):
    lines = markdown_body.strip().split("\n")
    html_parts = []
    in_table = False
    table_rows = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            # Split and clean parts
            parts = [p.strip() for p in stripped.split("|")[1:-1]]
            # Check if it is a separator line (e.g. | --- | --- |)
            if all(all(c == '-' or c == ':' or c == ' ' for c in part) for part in parts if part):
                continue
            table_rows.append(parts)
        else:
            if in_table:
                html_parts.append(render_html_table(table_rows))
                in_table = False
            # Render regular line
            if stripped == "":
                html_parts.append("<br/>")
            else:
                # Convert Markdown link syntax: [Text](Url) or [Text](mailto:Email)
                processed_line = stripped
                processed_line = re.sub(
                    r'\[([^\]]+)\]\(([^)]+)\)',
                    r'<a href="\2" style="color: #0284c7; text-decoration: none; font-weight: 500;">\1</a>',
                    processed_line
                )
                html_parts.append(
                    f"<p style='margin: 4px 0; font-family: \"Segoe UI\", Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; color: #334155; line-height: 1.6;'>{processed_line}</p>"
                )
                
    if in_table:
        html_parts.append(render_html_table(table_rows))
        
    body_content = "\n".join(html_parts)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="margin: 0; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9;">
        <div style="max-width: 700px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
            {body_content}
        </div>
    </body>
    </html>
    """
