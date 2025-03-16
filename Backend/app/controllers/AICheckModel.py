from app.services.autoDetectCheck import auto_detect_and_check

def aiChecker_model(message, user_text, bot):
    # Analyse the input with the auto_detect_and_check function
    result = auto_detect_and_check(user_text)

    if not result:
        bot.send_message(message.chat.id, "Error: Could not analyze the input. Please check the URL or file path.")
        return

    # Determine the type of input based on the API response.
    input_type = 'image'
    if "report" in result and "confidence" in result["report"]:
        input_type = 'voice'

    output = "===== RESULTS =====\n"

    if input_type == 'image':
        verdict = result["report"].get("verdict", "N/A")
        output += f"Verdict: {verdict.upper()}\n"

        if "ai" in result["report"] and "confidence" in result["report"]["ai"]:
            print(f"result of ai vs human: {result}")
            ai_confidence = result["report"]["ai"]["confidence"]
            human_confidence = result["report"]["human"]["confidence"]
            output += f"AI Likelihood: {ai_confidence:.2%}\n"

            if "generator" in result["report"]:
                output += "\nAI Generator Analysis:\n"
                for generator, details in result["report"]["generator"].items():
                    generator_name = generator.replace("_", " ").title()
                    confidence = details.get("confidence", 0)
                    is_detected = details.get("is_detected", False)
                    status = "DETECTED" if is_detected else "Not Detected"
                    output += f"  {generator_name}:\n   • {status} (confidence: {confidence:.2%})\n"

    elif input_type == 'voice':
        verdict = result["report"].get("verdict", "N/A")
        confidence = result["report"].get("confidence", 0)
        duration = result["report"].get("duration", 0)
        output += f"Verdict: {verdict.upper()}\n"
        output += f"Confidence: {confidence:.2%}\n"
        output += f"Audio Duration: {duration} seconds\n"

    else:
        output += "Unknown input type.\n"

    # Send the analysis result to the Telegram chat
    bot.send_message(message.chat.id, output)
