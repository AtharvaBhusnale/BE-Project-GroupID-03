import os

file_path = 'e:/MRI Enhancement/templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            // Wait for images to load to get dimensions
            iAfter.onload = function () {
                // Set container width to match image aspect ratio if needed, or just center it
                // For now, we rely on CSS height 400px.
                compareImages(divBefore);
            }'''

replacement = '''            // Wait for images to load to get dimensions
            const startComparison = () => {
                // Resize container to match image width so it centers correctly
                // and we don't have empty gray space
                container.style.width = iAfter.offsetWidth + "px";
                compareImages(divBefore);
            };

            if (iAfter.complete) {
                startComparison();
            } else {
                iAfter.onload = startComparison;
            }'''

# Normalize line endings and whitespace for matching
def normalize(s):
    return ' '.join(s.split())

if normalize(target) in normalize(content):
    # Try simple replace first
    if target in content:
        new_content = content.replace(target, replacement)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Successfully patched index.html')
    else:
        # Fallback to finding by markers
        start_marker = "// Wait for images to load to get dimensions"
        end_marker = "compareImages(divBefore);\n            }"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            end_idx += len(end_marker)
            original_block = content[start_idx:end_idx]
            new_content = content.replace(original_block, replacement)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('Successfully patched index.html via markers')
        else:
            print('Target block not found in index.html')
            print(f"Start index: {start_idx}, End index: {end_idx}")
else:
    print('Target content not found (normalized check failed)')
