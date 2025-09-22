import cairosvg
import os

def convert_svg_to_png(svg_path, png_path, width, height):
    try:
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width, output_height=height)
        print(f"Successfully converted {svg_path} to {png_path}")
    except Exception as e:
        print(f"Error converting {svg_path} to PNG: {e}")

if __name__ == "__main__":
    icons_dir = "assets/icons"
    
    # Define icons to convert
    icons_to_convert = {
        "add_expense_icon.svg": "add_expense_icon.png",
        # Add other icons here as you find them
    }

    for svg_file, png_file in icons_to_convert.items():
        svg_path = os.path.join(icons_dir, svg_file)
        png_path = os.path.join(icons_dir, png_file)
        convert_svg_to_png(svg_path, png_path, 24, 24)
