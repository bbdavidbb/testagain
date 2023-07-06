from pathlib import Path
import re
from html import escape


def import_secure_baseline(baseline_path=None):
    if baseline_path is None:
        baseline_path = Path(__file__).parent.parent.parent.parent / "baselines"

    product_names = [
        filename.stem
        for filename in baseline_path.glob("*.md")
    ]
    output = {}

    for product in product_names:
        output[product] = []
        product_path = baseline_path / f"{product}.md"
        with product_path.open("r") as f:
            md_lines = f.readlines()

        line_numbers = [
            int(re.search(r"## ([0-9]+)\.", line).group(1)) - 1
            for line in md_lines
            if re.search(r"^## [0-9]+\.", line)
        ]
        groups = [md_lines[line_number] for line_number in line_numbers]

        for group_name in groups:
            group = {}
            group_number = group_name.split(".")[0][3:]
            group_name = group_name.split(".")[1].strip()
            group["GroupNumber"] = group_number
            group["GroupName"] = group_name
            group["Controls"] = []

            id_regex = rf"#### MS\.{product.upper()}\.{group_number}\.\d+v\d+\s*$"
            line_numbers = [
                int(re.search(r"\.md:(\d+):", match.line).group(1)) - 1
                for match in re.finditer(id_regex, "".join(md_lines))
            ]

            for line_number in line_numbers:
                line_advance = 1
                value = md_lines[line_number + line_advance].strip()

                while not value.endswith("."):
                    line_advance += 1
                    value += " " + md_lines[line_number + line_advance].strip()

                value = escape(value)
                line = md_lines[line_number].strip()[5:]

                deleted = False
                if line.endswith("X"):
                    deleted = True
                    line = line[:-1]
                    value = "[DELETED] " + value

                group["Controls"].append({"Id": line, "Value": value, "Deleted": deleted})

            output[product].append(group)

    return output
