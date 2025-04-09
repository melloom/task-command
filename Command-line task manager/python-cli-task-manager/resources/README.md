# Application Resources

This folder contains resources for building and packaging the application:

- `icon.ico` - Windows icon
- `icon.icns` - macOS icon
- `icon.png` - Linux/generic icon

These files are used when building standalone executables with PyInstaller.

## Creating Icons

### Windows (.ico)
1. Start with a high-resolution PNG image (at least 256x256 pixels)
2. Use an online converter like https://convertico.com/ or a tool like GIMP
3. Save as icon.ico in this directory

### macOS (.icns)
1. Create PNG images in multiple sizes: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
2. Use iconutil on macOS or online converters like https://cloudconvert.com/png-to-icns
3. Save as icon.icns in this directory

### Linux (.png)
1. Save a high-resolution PNG image (256x256 pixels recommended)
2. Name it icon.png and place in this directory