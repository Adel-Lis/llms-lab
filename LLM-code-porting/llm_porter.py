"""
LLM Code Porter - Handles AI-powered code translation
"""

import concurrent.futures
from typing import Tuple

from config import get_client
from setup_environment import get_system_info, get_compile_command


def system_prompt(language):
    return f"""
            Your task is to convert Python code into high performance {language} code.
            Respond only with {language} code. Do not provide any explanation other than occasional comments.
            The {language} response needs to produce an identical output in the fastest possible time.
        """

def user_prompt_for(python, porting_lang):
    system_info = get_system_info()
    compile_command = get_compile_command(porting_lang)
    
    return f"""
            Port this Python code to {porting_lang} with the fastest possible implementation that produces identical output in the least time.
            The system information is:
            {system_info}
            Your response will be written to a file and then compiled and executed; the compilation command is:
            {compile_command}
            Respond only with {porting_lang} code.
            Python code to port:

            ```python
            {python}
            ```
        """

def messages(python, language):
    return [
        {"role": "system", "content": system_prompt(language)},
        {"role": "user", "content": user_prompt_for(python, language)},
    ]

def port_to_language(model, python, port_language): 
    client = get_client(model)
    reasoning_effort = "high" if "gpt" in model else None

    response = client.chat.completions.create(
        model=model, 
        messages=messages(python, port_language), 
        reasoning_effort=reasoning_effort
    )
    reply = response.choices[0].message.content
    reply = reply.replace('```cpp','').replace('```rust','').replace('```java','').replace('```','')

    return reply

def port_all_languages(python_code, model):
    languages = ["C++", "Java", "Rust"]

    if not python_code.strip():
        return "// No Python code provided", "// No Python code provided", "// No Python code provided"
    
    # Port to all languages in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            lang: executor.submit(port_to_language, model, python_code, lang) for lang in languages
        }

        results = {}
        for lang, future in futures.items():
            try:
                results[lang] = future.result(timeout=120)
            except Exception as e:
                results[lang] = f"// Error porting to {lang}: {str(e)}"

    return results["C++"], results["Java"], results["Rust"]