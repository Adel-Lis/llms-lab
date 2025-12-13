DEFAULT_PYTHON = '''# Be careful to support large numbers

def lcg(seed, a=1664525, c=1013904223, m=2**32):
    value = seed
    while True:
        value = (a * value + c) % m
        yield value

def max_subarray_sum(n, seed, min_val, max_val):
    lcg_gen = lcg(seed)
    random_numbers = [next(lcg_gen) % (max_val - min_val + 1) + min_val for _ in range(n)]
    max_sum = float('-inf')
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += random_numbers[j]
            if current_sum > max_sum:
                max_sum = current_sum
    return max_sum

def total_max_subarray_sum(n, initial_seed, min_val, max_val):
    total_sum = 0
    lcg_gen = lcg(initial_seed)
    for _ in range(20):
        seed = next(lcg_gen)
        total_sum += max_subarray_sum(n, seed, min_val, max_val)
    return total_sum

# Parameters
n = 10000        # Number of random numbers
initial_seed = 42  # Initial seed for the LCG
min_val = -10    # Minimum value of random numbers
max_val = 10     # Maximum value of random numbers

# Timing the function
import time
start_time = time.time()
result = total_max_subarray_sum(n, initial_seed, min_val, max_val)
end_time = time.time()

print("Total Maximum Subarray Sum (20 runs):", result)
print("Execution Time: {:.6f} seconds".format(end_time - start_time))
'''

CUSTOM_CSS = """
/* Main container styling */
.gradio-container {
    background: linear-gradient(135deg, #0a0a0a 0%, #0d1a0d 100%) !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
}

/* Header styling */
.app-header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(90deg, #0a1a0a, #0d1f0d);
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #1a3a1a;
}

.app-header h1 {
    color: #00ff88 !important;
    font-size: 2.5em !important;
    margin: 0 !important;
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.app-header p {
    color: #6a9a6a !important;
    margin-top: 8px !important;
}

/* Code editor styling */
.code-editor textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 13px !important;
    background-color: #0a0f0a !important;
    color: #b0d0b0 !important;
    border: 2px solid #1a3a1a !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

.code-editor textarea:focus {
    border-color: #00ff88 !important;
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
}

/* Tab styling */
.tabs {
    background: #0a0f0a !important;
    border-radius: 12px !important;
    border: 2px solid #1a3a1a !important;
}

.tab-nav {
    background: #050a05 !important;
    border-radius: 10px 10px 0 0 !important;
}

.tab-nav button {
    color: #6a9a6a !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
}

.tab-nav button.selected {
    background: linear-gradient(180deg, #1a3a1a 0%, #0a0f0a 100%) !important;
    color: #00ff88 !important;
    border-bottom: 3px solid #00ff88 !important;
}

/* Hide the label under tabs */
.tabs .tabitem > .label-wrap {
    display: none !important;
}

.tabs .tabitem > div > .label-wrap {
    display: none !important;
}

/* Button styling */
.primary-btn {
    background: linear-gradient(135deg, #00aa55 0%, #00ff88 100%) !important;
    border: none !important;
    color: #000 !important;
    font-weight: 700 !important;
    padding: 12px 32px !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4) !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 255, 136, 0.6) !important;
}

.primary-btn:disabled {
    background: linear-gradient(135deg, #1a3a1a 0%, #2a4a2a 100%) !important;
    color: #4a6a4a !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
    transform: none !important;
}

.secondary-btn {
    background: linear-gradient(135deg, #0a1a0a 0%, #0d1f0d 100%) !important;
    border: 2px solid #00ff88 !important;
    color: #00ff88 !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

.secondary-btn:hover {
    background: #00ff88 !important;
    color: #000 !important;
}

.secondary-btn:disabled {
    border-color: #2a4a2a !important;
    color: #4a6a4a !important;
    cursor: not-allowed !important;
}

/* Language labels */
.lang-label {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 12px;
    margin-bottom: 8px;
}

.cpp-label {
    background: #00599C;
    color: white;
}

.java-label {
    background: #f89820;
    color: white;
}

.rust-label {
    background: #CE422B;
    color: white;
}

/* Model dropdown */
.model-dropdown select {
    background: #0a0f0a !important;
    color: #b0d0b0 !important;
    border: 2px solid #1a3a1a !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

/* File upload - full width compact style */
.file-upload {
    min-height: 87px !important;
    max-height: 87px !important;
}

.file-upload > div {
    height: 100% !important;
}

.file-upload .wrap,
.file-upload .wrap > div,
.file-upload [data-testid="block"] {
    height: 85px !important;
    min-height: 85px !important;
    max-height: 85px !important;
}

.file-upload .wrap {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #0a0f0a !important;
    border: 2px solid #1a3a1a !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    width: 100% !important;
    cursor: pointer !important;
}

.file-upload .wrap:hover {
    border-color: #00ff88 !important;
}

/* Hide ALL default content inside file upload */
.file-upload .wrap > * {
    display: none !important;
}

/* Show custom centered text */
.file-upload .wrap::before {
    content: "+ Upload .py" !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #4a6a4a !important;
    font-size: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    width: 100% !important;
    height: 100% !important;
}

.file-upload .wrap:hover::before {
    color: #00ff88 !important;
}

/* Result panel styling */
.result-panel {
    background: #0a0f0a !important;
    border-radius: 8px !important;
    border: 2px solid #1a3a1a !important;
    padding: 16px !important;
    color: #b0d0b0 !important;
}

/* Graph placeholder */
.graph-placeholder {
    background: linear-gradient(135deg, #0a0f0a 0%, #050a05 100%);
    border: 2px dashed #1a3a1a;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    color: #4a6a4a;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0a0f0a;
}

::-webkit-scrollbar-thumb {
    background: #1a3a1a;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #00ff88;
}

/* Labels and text */
label {
    color: #b0d0b0 !important;
    font-weight: 600 !important;
}

/* Markdown text */
.result-panel h3 {
    color: #00ff88 !important;
}

.result-panel strong {
    color: #00ff88 !important;
}

/* Section header */
.section-header {
    margin-top: 24px;
    padding: 16px;
    background: #0a0f0a;
    border-radius: 12px;
    border: 2px solid #1a3a1a;
}

.section-header h3 {
    color: #00ff88;
    margin: 0 0 16px 0;
}
"""