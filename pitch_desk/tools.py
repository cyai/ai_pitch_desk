TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to Taj Halsani when the user wants to connect with him or want to get to know more about the product or the company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheduleTime": {
                        "type": "string",
                        "description": "When the user wants to schedule a meeting with Taj Halsani.",
                    }
                },
                "required": ["scheduleTime"],
            },
        },
    },
]
