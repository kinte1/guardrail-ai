from presidio_analyzer import AnalyzerEngine

def process_and_vault_prompt(user_prompt: str) -> tuple[str, dict]:
    """
    Scans a prompt for secrets using Presidio, then manually replaces them
    with unique tracking tokens to build a completely reliable local vault.
    """
    analyzer = AnalyzerEngine()

    # 1. Detect the secrets while text indices are unaltered
    analysis_results = analyzer.analyze(text=user_prompt, language="en")
    
    # Sort results in reverse order of appearance so when we modify text,
    # it doesn't mess up the indices of the secrets further down the string.
    sorted_results = sorted(analysis_results, key=lambda x: x.start, reverse=True)
    
    clean_text = user_prompt
    vault = {}
    
    # 2. Iterate and replace secrets with precise tokens
    for i, result in enumerate(sorted_results):
        original_value = user_prompt[result.start:result.end]
        
        # Skip empty extractions to ensure a bug like the blank key never happens
        if not original_value.strip():
            continue
            
        # Create a unique, unbreakable tracking token
        placeholder = f"__GUARDRAIL_SECRET_{i}__"
        
        # Replace the secret in the text string safely using coordinate slicing
        clean_text = clean_text[:result.start] + placeholder + clean_text[result.end:]
        
        # Save it into our local vault map
        vault[placeholder] = original_value

    return clean_text, vault

def restore_ai_response(ai_response: str, vault: dict) -> str:
    """
    Safely unpacks the vault map and restores the true variables into the text.
    """
    restored_text = ai_response
    for placeholder, original_value in vault.items():
        restored_text = restored_text.replace(placeholder, original_value)
    return restored_text


# --- Test the Complete Two-Way Guardrail Cycle ---
if __name__ == "__main__":
    original_prompt = "Tell my lawyer John Doe that my secret code is 555-0199."
    print("1. USER PROMPT SENT:")
    print(original_prompt)
    print("\n" + "-"*40)
    
    # Step A: Secure the prompt before sending to any cloud LLM
    clean_prompt, secret_vault = process_and_vault_prompt(original_prompt)
    print("2. CLEAN PROMPT TO BE SENT TO LLM:")
    print(clean_prompt)
    print("\n🔒 LOCAL VAULT MAP GENERATED:")
    print(secret_vault)
    print("\n" + "-"*40)
    
    # Step B: Dynamically build a mock response using whatever tokens were generated
    token_list = list(secret_vault.keys())
    if token_list:
        # Join tokens cleanly for simulation
        tokens_joined = ", ".join(token_list)
        mock_ai_response = f"I have processed the request for the user identified by system placeholder: {tokens_joined}."
    else:
        mock_ai_response = "No private tokens found to simulate in this message."
        
    print("3. RESPONSE RECEIVED FROM AI (Using tracking tokens):")
    print(mock_ai_response)
    print("\n" + "-"*40)
    
    # Step C: Re-inject original private data safely locally
    final_output = restore_ai_response(mock_ai_response, secret_vault)
    print("4. FINAL RESTORED PROMPT SHOWING TO USER:")
    print(final_output)